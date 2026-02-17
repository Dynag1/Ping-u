# -*- coding: utf-8 -*-
"""
Centralisation des classes et objets factices pour le mode headless (sans interface graphique).
Permet d'exécuter Ping ü sur des serveurs Linux sans PySide6 installé.
"""
import sys
import os
import threading

# Détecter si on doit forcer le mode headless
# Détecter si on doit forcer le mode headless
force_headless = "--headless" in sys.argv or "-headless" in sys.argv or "--start" in sys.argv or "-start" in sys.argv or "--stop" in sys.argv or "-stop" in sys.argv or "--reset-admin" in sys.argv or "HEADLESS" in os.environ

GUI_AVAILABLE = False
if not force_headless:
    try:
        from PySide6.QtCore import QObject, Signal, QThread, Qt, QTimer, QPoint, QModelIndex, QEvent, QCoreApplication, QLocale, QAbstractItemModel, QRunnable, QThreadPool, QMutex, QMutexLocker, Slot, QSortFilterProxyModel, QTranslator
        from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush, QAction, QActionGroup, QIcon
        from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView, QAbstractItemView, QMessageBox, QMenu, QFileDialog, QWidget, QDialog, QTimeEdit
        from src.ui_mainwindow import Ui_MainWindow
        pyqtSlot = Slot # Alias pour compatibilité
        GUI_AVAILABLE = True
    except (ImportError, Exception):
        GUI_AVAILABLE = False

# Toujours importer AppColors pour le re-exporter
try:
    from src.utils.colors import AppColors
except ImportError:
    class AppColors:
        VERT_PALE = "#d4edda"
        JAUNE_PALE = "#fff3cd"
        ORANGE_PALE = "#ffe5b4"
        ROUGE_PALE = "#f8d7da"
        NOIR_GRIS = "#343a40"
        BG_FRAME_HAUT = "#f8f9fa"
        BG_FRAME_MID = "#e9ecef"
        BG_FRAME_DROIT = "#dee2e6"
        BG_BUT = "#ffffff"

if not GUI_AVAILABLE:
    class QAbstractItemModel: pass
    def Slot(*args, **kwargs): return lambda f: f
    def pyqtSlot(*args, **kwargs): return lambda f: f
    
    class QRunnable:
        def __init__(self, *args): pass
        def setAutoDelete(self, val): pass
        def run(self): pass
    
    class QThreadPool:
        @staticmethod
        def globalInstance():
            class DummyPool:
                def setMaxThreadCount(self, n): pass
                def start(self, worker): 
                    # Exécution directe ou via thread
                    t = threading.Thread(target=worker.run, daemon=True)
                    t.start()
                def waitForDone(self): pass
                def clear(self): pass
            return DummyPool()
            
    class QMutex:
        def __init__(self): self._lock = threading.Lock()
        def lock(self): self._lock.acquire()
        def unlock(self): self._lock.release()
        
    class QMutexLocker:
        def __init__(self, mutex): 
            self._mutex = mutex
        def __enter__(self): 
            if hasattr(self._mutex, 'lock'): self._mutex.lock()
            return self
        def __exit__(self, *args): 
            if hasattr(self._mutex, 'unlock'): self._mutex.unlock()
    class Signal:
        """Signal factice fonctionnel pour le mode headless"""
        def __init__(self, *args):
            self._callbacks = []
        def emit(self, *args):
            for callback in self._callbacks:
                try:
                    callback(*args)
                except Exception as e:
                    print(f"Signal emit error: {e}")
        def connect(self, callback):
            self._callbacks.append(callback)

    class QObject:
        def __init__(self, *args, **kwargs):
            pass

    class QThread:
        """QThread fonctionnel pour mode headless utilisant threading.Thread"""
        def __init__(self, *args, **kwargs):
            self._thread = None
            self._running = False
            self.finished = Signal()
        
        def start(self):
            self._running = True
            self._thread = threading.Thread(target=self._run_wrapper, daemon=True)
            self._thread.start()
        
        def _run_wrapper(self):
            try:
                self.run()
            finally:
                self._running = False
                self.finished.emit()
        
        def run(self):
            """À surcharger dans les sous-classes"""
            pass

        def wait(self, msecs=None):
            """Attend la fin du thread (timeout en ms)"""
            if self._thread and self._thread.is_alive():
                timeout = None
                if msecs is not None:
                    timeout = msecs / 1000.0
                
                self._thread.join(timeout)
                return not self._thread.is_alive()
            return True
        
        def isRunning(self):
            return self._running and self._thread and self._thread.is_alive()
        
        def quit(self):
            self._running = False

    class QStandardItem:
        def __init__(self, text=""):
            self._text = str(text)
            self._data = {0: self._text} # 0 is Qt.DisplayRole
        def text(self): return self._text
        def setText(self, t): 
            self._text = str(t)
            self.setData(self._text, 0) # Qt.DisplayRole = 0
        def setData(self, value, role=0): self._data[role] = value
        def data(self, role=0): 
            if role == 0 and 0 not in self._data:
                 return self._text
            return self._data.get(role)
        def setBackground(self, brush): pass
        def setForeground(self, brush): pass
        def setCheckable(self, b): pass
        def setEditable(self, b): pass
        def setSelectable(self, b): pass
        def setEnabled(self, b): pass
        def checkState(self): return 0
        def setCheckState(self, s): pass

    class QStandardItemModel(QObject):
        def __init__(self, *args):
            super().__init__()
            self._rows = []
            self._headers = []
            self._column_count = 0
            self.dataChanged = Signal(object, object, list)
            self.rowsInserted = Signal(object, int, int)
            self.rowsRemoved = Signal(object, int, int)

        def rowCount(self, parent=None): return len(self._rows)
        def columnCount(self, parent=None): return self._column_count
        
        def clear(self):
            self._rows = []
            self._column_count = 0
            
        def setHorizontalHeaderLabels(self, labels):
            self._headers = [QStandardItem(l) for l in labels]
            if len(labels) > self._column_count:
                self._column_count = len(labels)
                
        def horizontalHeaderItem(self, col):
            return self._headers[col] if col < len(self._headers) else QStandardItem("")
            
        def item(self, row, col=0):
            if row < len(self._rows) and col < len(self._rows[row]):
                return self._rows[row][col]
            return None
            
        def setItem(self, row, col, item):
            while len(self._rows) <= row:
                self._rows.append([])
            while len(self._rows[row]) <= col:
                self._rows[row].append(QStandardItem(""))
            
            self._rows[row][col] = item
            
            # Emission signal (topLeft, bottomRight, roles)
            idx = self.index(row, col)
            self.dataChanged.emit(idx, idx, [])

        def appendRow(self, items):
            if not isinstance(items, list):
                items = [items]
            row_idx = len(self._rows)
            self._rows.append(items)
            if len(items) > self._column_count:
                self._column_count = len(items)
            self.rowsInserted.emit(None, row_idx, row_idx)

        def removeRow(self, row):
            if 0 <= row < len(self._rows):
                del self._rows[row]
                self.rowsRemoved.emit(None, row, row)

        def removeRows(self, row, count, parent=None):
            if 0 <= row < len(self._rows):
                end = min(row + count, len(self._rows))
                del self._rows[row:end]
                self.rowsRemoved.emit(None, row, row + count - 1)
            return True

        def removeColumns(self, col, count, parent=None):
            for row in self._rows:
                if 0 <= col < len(row):
                    end = min(col + count, len(row))
                    del row[col:end]
            return True

        def index(self, row, col, parent=None):
            return QModelIndex(row, col)
            
        def data(self, index, role=0):
            item = self.item(index.row(), index.column())
            return item.data(role) if item else None

    class QPoint: pass
    class QModelIndex:
        def __init__(self, row=-1, col=-1):
            self._row = row
            self._col = col
        def row(self): return self._row
        def column(self): return self._col
        def isValid(self): return self._row >= 0 and self._col >= 0

    class QColor:
        def __init__(self, *args): pass
    class QBrush:
        def __init__(self, *args): pass
    class QAction: pass
    class QActionGroup: pass
    class QMainWindow: pass
    class QTranslator:
        def __init__(self, *args, **kwargs): pass
        def load(self, *args, **kwargs): return False
    
    class QCoreApplication:
        @staticmethod
        def instance(): return None
        @staticmethod
        def translate(context, text, disambiguation=None, n=-1): return text
        @staticmethod
        def processEvents(): pass
        @staticmethod
        def applicationDirPath(): return os.path.dirname(os.path.abspath(sys.argv[0]))
    
    class QLocale:
        def __init__(self, *args): pass
        def name(self): return "fr_FR"
    
    class QIcon:
        def __init__(self, *args): pass
        def addFile(self, *args, **kwargs): pass
    
    class QEvent:
        LanguageChange = 0
    
    class Qt:
        DisplayRole = 0
        ItemIsEditable = 0
        BackgroundRole = 0
        UserRole = 0
        AlignCenter = 0
        NoBrush = 0

    class QTimer:
        def __init__(self):
            self.timeout = Signal()
            self._timer = None
            self._interval = 1000
            self._running = False
            
        def start(self, ms=None):
            if ms is not None:
                self._interval = ms
            self._running = True
            self._schedule()
            
        def stop(self):
            self._running = False
            if self._timer:
                self._timer.cancel()
                self._timer = None
                
        def setInterval(self, ms):
            self._interval = ms
            # Si le timer tourne, on redémarre avec le nouvel intervalle au prochain tick
            # Mais pour être plus réactif, on peut aussi annuler et relancer
            if self._running:
                self._schedule()
            
        def interval(self):
            return self._interval
            
        def _schedule(self):
            if not self._running: return
            if self._timer: self._timer.cancel()
            
            # Utiliser threading.Timer pour l'exécution différée
            self._timer = threading.Timer(self._interval / 1000.0, self._tick)
            self._timer.daemon = True
            self._timer.start()
            
        def _tick(self):
            if self._running:
                # Émettre le signal via QThread si possible, ou direct
                self.timeout.emit()
                self._schedule()

        @staticmethod
        def singleShot(ms, callback):
            timer = threading.Timer(ms / 1000.0, callback)
            timer.daemon = True
            timer.start()

    class Ui_MainWindow:
        def setupUi(self, obj): pass
        def retranslateUi(self, obj): pass

    class QAbstractItemView:
        NoSelection = 0
    
    class QHeaderView:
        Fixed = 0
        Stretch = 1
        ResizeToContents = 2
    
    class QFileDialog:
        @staticmethod
        def getSaveFileName(*args, **kwargs): return ("", "")
        @staticmethod
        def getOpenFileName(*args, **kwargs): return ("", "")
    
    class QMessageBox:
        @staticmethod
        def information(*args, **kwargs): pass
        @staticmethod
        def warning(*args, **kwargs): pass
        @staticmethod
        def critical(*args, **kwargs): pass
        @staticmethod
        def question(*args, **kwargs): return 0
        Ok = 1
        Yes = 2
        No = 3
        Accepted = 1
        Rejected = 0

    class QDialog:
        def __init__(self, *args): pass
        def exec(self): return 0
        Accepted = 1
        Rejected = 0

    class QTimeEdit:
        def __init__(self, *args): pass
        def setTime(self, t): pass
        def time(self): 
            class DummyTime:
                def toPython(self): return None
            return DummyTime()

    class QMenu:
        def __init__(self, *args): pass
        def addAction(self, *args): pass
        def exec(self, *args): pass
    
    class QWidget:
        def __init__(self, *args): pass
        def setVisible(self, v): pass
        def show(self): pass
        def hide(self): pass
        def layout(self): return None
        def setLayout(self, l): pass
        def setEnabled(self, e): pass

    class QSortFilterProxyModel:
        def __init__(self, *args): pass
        def setSourceModel(self, m): pass
        def sourceModel(self): return None
        def mapToSource(self, i): return i
        def mapFromSource(self, i): return i
        def setFilterFixedString(self, s): pass
        def setFilterKeyColumn(self, c): pass

    class QApplication:
        def __init__(self, *args):
            self._running = True
        @staticmethod
        def instance(): return None
        @staticmethod
        def processEvents(): pass
        def exec(self): return 0
        def quit(self): 
            self._running = False
        def installTranslator(self, t): pass
        def removeTranslator(self, t): pass

# Exportation des symboles
if not GUI_AVAILABLE:
    # On s'assure que les classes dummies sont bien dans le module pour l'import from
    pass
