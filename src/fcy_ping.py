from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, QTimer, Qt, QMutex, QMutexLocker
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush
import concurrent.futures
import pythonping as ping
import time
import multiprocessing
import src.var as var


class PingWorker(QRunnable):
    class Signals(QObject):
        result = Signal(str, float, str)  # ip, latence, couleur
        finished = Signal()

    def __init__(self, ip, comm):
        super().__init__()
        self.ip = ip
        self.comm = comm
        self.signals = self.Signals()
        self._stop_flag = False
        self.mutex = QMutex()

    def stop(self):
        with QMutexLocker(self.mutex):
            self._stop_flag = True

    def run(self):
        try:
            # Vérification initiale
            if not var.tourne or self._stop_flag:
                return
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    ping.ping,
                    self.ip,
                    size=1,
                    count=1,
                    timeout=0.5
                )

                # Vérification périodique pendant l'exécution
                while not future.done():
                    if self._stop_flag or not var.tourne:
                        future.cancel()
                        return
                    time.sleep(0.1)  # Vérification toutes les 100ms

                result = future.result()

                # Traitement du résultat
                if self._stop_flag:
                    return

                if result.rtt_avg_ms == 500:
                    self.signals.result.emit(self.ip, 500, "#787878")
                    try:
                        self.list_increment(var.liste_hs, self.ip)
                        self.list_increment(var.liste_mail, self.ip)
                        self.list_increment(var.liste_telegram, self.ip)
                    except Exception as inst:
                        print((inst))
                else:
                    color = self.get_color(result.rtt_avg_ms)
                    self.signals.result.emit(self.ip, result.rtt_avg_ms, color)
                    try:
                        self.list_ok(var.liste_hs, self.ip)
                        self.list_ok(var.liste_mail, self.ip)
                        self.list_ok(var.liste_telegram, self.ip)
                    except Exception as inst:
                        print((inst))

        except (concurrent.futures.CancelledError, Exception) as e:
            if not isinstance(e, concurrent.futures.CancelledError):
                print(f"Erreur thread: {e}")
        finally:
            self.signals.finished.emit()

    def list_increment(self, liste, ip):
        try:
            if ip in liste:
                if int(liste[ip]) < int(var.nbrHs):
                    liste[ip] += 1
                else:
                    liste[ip] = liste[ip]
            else:
                liste[ip] = 1
        except Exception as inst:
            print((inst))

    def list_ok(self, liste, ip):
        try:
            if ip in liste:
                if liste[ip] == 10:
                    liste[ip] = 20
                else:
                    try:
                        del var.liste[ip]
                    except:
                        pass
        except Exception as inst:
            print((inst))

    def get_color(self, latency):
        if latency < 2: return "#00FF00"
        elif latency < 10: return "#FFFF00"
        elif latency < 50: return "#FFA500"
        else: return "#FF0000"

class PingManager(QObject):
    def __init__(self, tree_widget):
        super().__init__()
        self.tree_widget = tree_widget
        self.thread_pool = QThreadPool()
        #self.thread_pool.setMaxThreadCount(1)
        self.thread_pool.setMaxThreadCount(multiprocessing.cpu_count() * 2)
        self.workers = []
        self.timer = None
        self.mutex = QMutex()

    def start(self):
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.process_all_ips)
        self.process_all_ips()
        self.timer.start(var.delais * 1000)  # delais doit être en secondes
        print(self.timer)

    def stop(self):
        if self.timer and self.timer.isActive():
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None

        # Arrêt de tous les workers
        for worker in self.workers[:]:
            worker.stop()

        # Nettoyage
        self.thread_pool.clear()
        self.workers.clear()

    def process_all_ips(self):
        if not var.tourne:
            return

        root = self.tree_widget.invisibleRootItem()
        for row in range(root.rowCount()):
            ip_item = root.child(row, 1)
            if ip_item:
                worker = PingWorker(ip_item.text(), self)
                worker.signals.result.connect(self.handle_result)
                worker.signals.finished.connect(lambda w=worker: self.remove_worker(w))
                self.workers.append(worker)
                self.thread_pool.start(worker)

    def remove_worker(self, worker):
        if worker in self.workers:
            self.workers.remove(worker)


    def handle_result(self, ip, latency, color):
        row = self.find_item_row(ip)
        if row == -1:
            return

        # Met à jour toutes les colonnes
        for col in range(self.tree_widget.columnCount()):
            item = self.tree_widget.item(row, col)
            # Crée l'item si inexistant
            if not item:
                item = QStandardItem()
                self.tree_widget.setItem(row, col, item)
            # Applique la couleur seulement à la colonne de latence
            if col == 5:  # Colonne Latence (index 4)
                item.setText(f"{latency:.1f} ms" if latency < 500 else "HS")
            # Colorie toute la ligne
            item.setBackground(QBrush(QColor(color)))

    def find_item_row(self, ip):
        """Trouve la ligne correspondant à l'IP dans le modèle"""
        for row in range(self.tree_widget.rowCount()):
            ip_item = self.tree_widget.item(row, 1)  # Colonne IP (index 1)
            if ip_item and ip_item.text() == ip:
                return row
        return -1

    def find_item(self, ip):
            """Version sécurisée avec vérifications"""
            try:
                if not hasattr(self, 'tree_widget'):
                    print("ERREUR: QTreeWidget non initialisé")
                    return None

                # Recherche exacte dans la colonne 1
                items = self.tree_widget.findItems(ip, Qt.MatchFlag.MatchExactly, 1)

                if not items:
                    print(f"Aucun item trouvé pour l'IP: {ip}")
                    return None

                return items[0]

            except Exception as e:
                print(f"Erreur dans find_item: {str(e)}")
                return None
