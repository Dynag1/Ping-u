from src.utils.headless_compat import (
    GUI_AVAILABLE, QObject, QRunnable, QThreadPool, QMutex, QMutexLocker, Signal, Slot, pyqtSlot,
    QStandardItem, QApplication
)

from src import ip_fct
import multiprocessing

class IpManager(QObject):
    _instance = None
    _class_mutex = QMutex()
    _instance_mutex = QMutex()

    @classmethod
    def instance(cls):
        if not cls._instance:
            locker = QMutexLocker(cls._class_mutex)
            if not cls._instance:
                cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.thread_count = 0

    def increment(self):
        locker = QMutexLocker(self._instance_mutex)
        self.thread_count += 1

    def decrement(self):
        locker = QMutexLocker(self._instance_mutex)
        self.thread_count -= 1

    def count(self):
        locker = QMutexLocker(self._instance_mutex)
        return self.thread_count

class IpWorker(QRunnable):
    def __init__(self, ip, config, signals):
        super().__init__()
        self.ip = ip
        self.config = config
        self.signals = signals
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self):
        print("run")
        try:
            IpManager.instance().increment()
            IpManager.instance().increment()
            print("run")
            result = ip_fct.ipPing(self.ip)
            print(result)
            if result != "OK":

                return

            nom = mac = port_info = ""
            if self.config['resolve_host']:
                try:
                    nom = ip_fct.socket.gethostbyaddr(self.ip)[0]
                except:
                    pass
            if self.config['get_mac']:
                mac = ip_fct.getmac(self.ip) or ""
            if self.config['check_port']:
                port_info = ip_fct.check_port(self.ip, self.config['port']) or ""

            self.signals.data_ready.emit({
                'ip': self.ip,
                'nom': nom,
                'mac': mac,
                'port': port_info
            })
            print("test" + self.ip)
            self.signals.data_ready.emit({...})

        except Exception as e:
            self.signals.error.emit(f"Erreur avec {self.ip}: {str(e)}")
        finally:
            print(IpManager.instance().count())
            self.signals.progression.emit(IpManager.instance().count())
            IpManager.instance().decrement()

class IpScanner(QObject):
    data_ready = Signal(dict)
    progression = Signal(int)
    error = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool.globalInstance()
        try:
            import multiprocessing
            self.threadpool.setMaxThreadCount(multiprocessing.cpu_count() * 2)
        except:
            pass
        self._running = False
        if GUI_AVAILABLE:
            self.moveToThread(QApplication.instance().thread())

    @Slot(str, int, str, dict)
    def scan(self, base_ip, count, port, options):
        self._running = True
        IpManager.instance().thread_count = 0

        try:
            for i in range(count):
                if not self._running:
                    break

                ip = self._generate_ip(base_ip, i)
                worker = IpWorker(ip, {
                    'port': port,
                    'resolve_host': options.get('resolve_host', False),
                    'get_mac': options.get('get_mac', False),
                    'check_port': options.get('check_port', False)
                }, self)
                self.threadpool.start(worker)

            self.threadpool.waitForDone()
        finally:
            self.finished.emit()

    def _generate_ip(self, base_ip, offset):
        octets = list(map(int, base_ip.split('.')))
        octets[3] += offset

        for i in reversed(range(2, 4)):
            carry, octets[i] = divmod(octets[i], 256)
            if i > 0:
                octets[i-1] += carry

        if octets[0] > 255 or octets[1] > 255:
            raise ValueError("Adresse IP hors plage valide")

        return ".".join(map(str, octets[:4]))

    @Slot()
    def stop(self):
        self._running = False
        self.threadpool.clear()
