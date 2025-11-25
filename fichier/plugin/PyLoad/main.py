import sys
import winreg
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTreeView,
    QLabel, QPushButton, QMainWindow, QMessageBox
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

# Emplacements des programmes au démarrage dans le registre
STARTUP_LOCATIONS = [
    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
]

def get_startup_programs():
    """Retourne une liste de tuples (nom, commande, clé, root)"""
    programs = []
    for root, path in STARTUP_LOCATIONS:
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        programs.append((name, value, path, root))
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue
    return programs

class StartupProgramsWidget(QWidget):
    def __init__(self, comm, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Programmes au démarrage")
        self.resize(700, 400)

        layout = QVBoxLayout(self)

        label = QLabel("Liste des programmes exécutés au démarrage :")
        layout.addWidget(label)

        self.tree = QTreeView()
        layout.addWidget(self.tree)

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Activé", "Nom", "Commande", "Clé de registre"])
        self.tree.setModel(self.model)
        self.tree.setSortingEnabled(True)

        self.populate()
        self.quitButton = QPushButton("Quitter")
        self.quitButton.clicked.connect(lambda: self.quit(comm))
        layout.addWidget(self.quitButton)

        # Connexion du changement d'état de la checkbox
        self.model.itemChanged.connect(self.on_item_changed)

    def quit(self, comm):
        comm.relaodWindow.emit(True)

    def populate(self):
        self.model.blockSignals(True)
        self.model.removeRows(0, self.model.rowCount())

        # Récupérer tous les programmes et organiser par clé de registre pour gérer les activations/désactivations
        programs = get_startup_programs()

        # Pour gérer les doublons (même nom dans plusieurs clés), on liste tous
        for name, value, path, root in programs:
            # Case à cocher activée car la valeur existe
            check_item = QStandardItem()
            check_item.setCheckable(True)
            check_item.setCheckState(Qt.Checked)
            check_item.setEditable(False)

            name_item = QStandardItem(name)
            name_item.setEditable(False)

            value_item = QStandardItem(value)
            value_item.setEditable(False)

            path_item = QStandardItem(path)
            path_item.setEditable(False)

            # Stocker infos pour gestion dans l'item checkable
            check_item.setData((name, value, path, root), role=Qt.UserRole)

            self.model.appendRow([check_item, name_item, value_item, path_item])

        self.model.blockSignals(False)

    def on_item_changed(self, item):
        # On ne traite que les changements sur la colonne "Activé"
        if item.column() != 0:
            return
        data = item.data(Qt.UserRole)
        if not data:
            return

        name, value, path, root = data
        checked = item.checkState() == Qt.Checked

        try:
            if checked:
                # Activer : écrire la valeur dans le registre
                with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            else:
                # Désactiver : supprimer la valeur dans le registre
                with winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
        except PermissionError:
            QMessageBox.warning(self, "Erreur", "Permission refusée : lancez le programme en administrateur.")
            # Revenir à l'état précédent (inverser la checkbox)
            self.model.blockSignals(True)
            item.setCheckState(Qt.Checked if not checked else Qt.Unchecked)
            self.model.blockSignals(False)
        except FileNotFoundError:
            # Si la valeur n'existe plus, on ignore
            pass
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la modification : {e}")
            # Revenir à l'état précédent
            self.model.blockSignals(True)
            item.setCheckState(Qt.Checked if not checked else Qt.Unchecked)
            self.model.blockSignals(False)


def main(self, comm):
    self.uninstaller_plugin = StartupProgramsWidget(comm)
    self.setCentralWidget(self.uninstaller_plugin)
