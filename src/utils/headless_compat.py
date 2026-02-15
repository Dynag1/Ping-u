# -*- coding: utf-8 -*-
"""
Centralisation des classes et objets factices pour le mode headless (sans interface graphique).
Permet d'exécuter Ping ü sur des serveurs Linux sans PySide6 installé.
"""
import sys
import threading

try:
    from PySide6.QtCore import QObject, Signal, QThread, Qt, QTimer, QPoint, QModelIndex, QEvent
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QBrush, QAction, QActionGroup
    from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

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
        
        def wait(self, timeout_ms=None):
            if self._thread:
                timeout_sec = timeout_ms / 1000 if timeout_ms else None
                self._thread.join(timeout=timeout_sec)
                return not self._thread.is_alive()
            return True
        
        def isRunning(self):
            return self._running
        
        def quit(self):
            self._running = False
        
        def stop(self):
            self._running = False

    class QStandardItem:
        def __init__(self, text=""):
            self._text = str(text) if text else ""
            self._background = None
            self._foreground = None
            self._data = {}
            self._flags = 0
        def text(self): return self._text
        def setText(self, text): self._text = str(text)
        def setBackground(self, brush): self._background = brush
        def background(self): return self._background
        def setForeground(self, brush): self._foreground = brush
        def foreground(self): return self._foreground
        def setData(self, data, role=0): self._data[role] = data
        def data(self, role=0): return self._data.get(role)
        def setEditable(self, editable): pass
        def flags(self): return self._flags
        def setFlags(self, flags): self._flags = flags

    class QStandardItemModel:
        def __init__(self, *args):
            self._rows = []
            self._headers = []
            self._column_count = 0
            # Instanciation de vrais signaux
            self.rowsInserted = Signal(object, int, int)
            self.rowsRemoved = Signal(object, int, int)
            self.dataChanged = Signal(object, object, list)
            self.modelReset = Signal()

        def rowCount(self, parent=None): return len(self._rows)
        def columnCount(self, parent=None): return self._column_count
        
        def appendRow(self, items):
            row = len(self._rows)
            self._rows.append(items)
            if items and len(items) > self._column_count:
                self._column_count = len(items)
            # Emission signal (parent, first, last)
            self.rowsInserted.emit(QModelIndex(), row, row)
            
        def removeRows(self, start, count):
            if count <= 0: return
            del self._rows[start:start+count]
            self.rowsRemoved.emit(QModelIndex(), start, start + count - 1)

        def removeRow(self, row):
            if 0 <= row < len(self._rows):
                del self._rows[row]
                self.rowsRemoved.emit(QModelIndex(), row, row)

        def clear(self):
            self._rows = []
            self._column_count = 0
            self.modelReset.emit()

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

        def index(self, row, col, parent=None):
            return QModelIndex()
            
        def data(self, index, role=0):
            return None

    class QPoint: pass
    class QModelIndex: pass
    class QColor:
        def __init__(self, *args): pass
    class QBrush:
        def __init__(self, *args): pass
    class QAction: pass
    class QActionGroup: pass
    class QMainWindow: pass
    class QHeaderView: pass
    class QSortFilterProxyModel: pass
    class QApplication:
        def __init__(self, *args): pass
        @staticmethod
        def instance(): return None
    class QTranslator: pass
    
    class QEvent:
        LanguageChange = 0
    
    class Qt:
        DisplayRole = 0
        ItemIsEditable = 0
        BackgroundRole = 0
        UserRole = 0
        AlignCenter = 0

    class QTimer:
        @staticmethod
        def singleShot(ms, callback):
            timer = threading.Timer(ms / 1000, callback)
            timer.daemon = True
            timer.start()

    class Ui_MainWindow:
        def setupUi(self, obj): pass

# Exportation des symboles
if not GUI_AVAILABLE:
    # On s'assure que les classes factices sont disponibles sous les mêmes noms
    pass
