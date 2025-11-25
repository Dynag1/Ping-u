import sys
import os
import shutil
import subprocess
import ctypes
import winreg
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QPushButton, QMessageBox, QLabel, QApplication
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def relancer_en_admin():
    if sys.platform != "win32":
        return True  # Pas Windows, on continue

    if is_admin():
        return True  # Déjà admin

    params = " ".join([f'"{arg}"' for arg in sys.argv])
    executable = sys.executable
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", executable, params, None, 1)
    if ret <= 32:
        return False  # Refus ou erreur
    sys.exit(0)

class UninstallerPlugin(QWidget):
    def __init__(self, comm, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plugin : Gestionnaire de logiciels")
        self.resize(900, 600)
        self.layout = QVBoxLayout(self)

        self.label = QLabel("Cochez les logiciels à désinstaller puis cliquez sur 'Désinstaller sélectionnés' :")
        self.layout.addWidget(self.label)

        self.tree_view = QTreeView()
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.setAlternatingRowColors(True)
        self.layout.addWidget(self.tree_view)

        self.uninstall_button = QPushButton("Désinstaller sélectionnés")
        self.uninstall_button.clicked.connect(self.uninstall_selected)
        self.layout.addWidget(self.uninstall_button)

        self.refresh_button = QPushButton("Rafraîchir la liste")
        self.refresh_button.clicked.connect(self.populate_list)
        self.layout.addWidget(self.refresh_button)

        self.quitButton = QPushButton("Quitter")
        self.quitButton.clicked.connect(lambda: self.quit(comm))
        self.layout.addWidget(self.quitButton)

        self.populate_list()

    def quit(self, comm):
        comm.relaodWindow.emit(True)

    def get_installed_programs(self):
        uninstall_keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        programs = []

        for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for key_path in uninstall_keys:
                try:
                    key = winreg.OpenKey(root, key_path)
                except FileNotFoundError:
                    continue

                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        uninstall_str = None
                        size = None
                        install_date = None
                        version = None
                        try:
                            uninstall_str = winreg.QueryValueEx(subkey, "UninstallString")[0]
                        except FileNotFoundError:
                            uninstall_str = None
                        try:
                            size = winreg.QueryValueEx(subkey, "EstimatedSize")[0]  # Ko
                        except FileNotFoundError:
                            size = None
                        try:
                            install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]  # YYYYMMDD
                        except FileNotFoundError:
                            install_date = None
                        try:
                            version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                        except FileNotFoundError:
                            version = None

                        if name and uninstall_str:
                            programs.append({
                                "name": name,
                                "uninstall_string": uninstall_str,
                                "version": version,
                                "size": size,
                                "install_date": install_date
                            })
                        subkey.Close()
                    except OSError:
                        continue
                key.Close()

        # Supprimer doublons par nom
        seen = set()
        unique_programs = []
        for p in programs:
            if p["name"] not in seen:
                seen.add(p["name"])
                unique_programs.append(p)
        return unique_programs

    def format_size(self, size_kb):
        if size_kb is None:
            return ""
        try:
            size_kb = int(size_kb)
            if size_kb < 1024:
                return f"{size_kb} Ko"
            else:
                return f"{size_kb / 1024:.2f} Mo"
        except Exception:
            return ""

    def format_date(self, date_str):
        if not date_str or len(date_str) != 8:
            return ""
        try:
            year = date_str[0:4]
            month = date_str[4:6]
            day = date_str[6:8]
            return f"{day}/{month}/{year}"
        except Exception:
            return ""

    def populate_list(self):
        self.software_list = self.get_installed_programs()

        self.model = QStandardItemModel(0, 5, self)
        self.model.setHeaderData(0, Qt.Horizontal, "Sélection")
        self.model.setHeaderData(1, Qt.Horizontal, "Nom")
        self.model.setHeaderData(2, Qt.Horizontal, "Version")
        self.model.setHeaderData(3, Qt.Horizontal, "Taille")
        self.model.setHeaderData(4, Qt.Horizontal, "Date d'installation")

        for sw in self.software_list:
            name = sw.get("name", "Inconnu")
            version = sw.get("version") or ""
            size = self.format_size(sw.get("size"))
            install_date = self.format_date(sw.get("install_date"))

            item_check = QStandardItem()
            item_check.setCheckable(True)
            item_check.setEditable(False)
            item_check.setCheckState(Qt.Unchecked)

            item_name = QStandardItem(name)
            item_name.setEditable(False)

            item_version = QStandardItem(version)
            item_version.setEditable(False)

            item_size = QStandardItem(size)
            item_size.setEditable(False)

            item_date = QStandardItem(install_date)
            item_date.setEditable(False)

            self.model.appendRow([item_check, item_name, item_version, item_size, item_date])

        self.tree_view.setModel(self.model)
        for col in range(5):
            self.tree_view.resizeColumnToContents(col)

    def clean_residuals(self, software_name):
        reply = QMessageBox.question(
            self, "Nettoyage des résidus",
            f"Voulez-vous rechercher et supprimer les fichiers et clés de registre résiduels pour '{software_name}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]

        deleted_keys = []
        for root, path in reg_paths:
            try:
                key = winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
            except FileNotFoundError:
                continue

            for i in reversed(range(winreg.QueryInfoKey(key)[0])):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ)
                    try:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    except FileNotFoundError:
                        name = None
                    subkey.Close()
                    if name and software_name.lower() in name.lower():
                        try:
                            winreg.DeleteKey(key, subkey_name)
                            deleted_keys.append(subkey_name)
                        except OSError:
                            pass
                except OSError:
                    pass
            key.Close()

        possible_paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), software_name),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), software_name),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), software_name),
            os.path.join(os.environ.get("APPDATA", ""), software_name),
        ]

        deleted_dirs = []
        for folder in possible_paths:
            if folder and os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    deleted_dirs.append(folder)
                except Exception:
                    pass

        msg = f"Nettoyage terminé.\nClés supprimées : {len(deleted_keys)}\nDossiers supprimés : {len(deleted_dirs)}"
        QMessageBox.information(self, "Nettoyage des résidus", msg)

    def uninstall_selected(self):
        if not is_admin():
            QMessageBox.critical(self, "Droits administrateur requis",
                                 "Veuillez relancer le programme en mode administrateur pour désinstaller des logiciels.")
            return

        checked_indexes = []
        for row in range(self.model.rowCount()):
            item_check = self.model.item(row, 0)
            if item_check.checkState() == Qt.Checked:
                checked_indexes.append(row)

        if not checked_indexes:
            QMessageBox.information(self, "Aucun logiciel sélectionné", "Veuillez cocher au moins un logiciel à désinstaller.")
            return

        reply = QMessageBox.question(
            self, "Confirmation",
            f"Voulez-vous vraiment désinstaller {len(checked_indexes)} logiciel(s) sélectionné(s) ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        errors = []
        for row in checked_indexes:
            sw = self.software_list[row]
            name = sw.get("name", "Inconnu")
            uninstall_str = sw.get("uninstall_string")

            print(f"[DEBUG] Logiciel: {name}")
            print(f"[DEBUG] Commande brute de désinstallation: {uninstall_str}")

            if not uninstall_str:
                errors.append(f"Aucune commande de désinstallation trouvée pour {name}.")
                continue

            uninstall_str = uninstall_str.strip()
            if uninstall_str.startswith('"') and uninstall_str.endswith('"'):
                uninstall_str = uninstall_str[1:-1]

            try:
                subprocess.Popen(uninstall_str, shell=True)
            except Exception as e:
                errors.append(f"Erreur lors de la désinstallation de {name} : {e}")

        if errors:
            QMessageBox.warning(self, "Erreurs", "\n".join(errors))
        else:
            QMessageBox.information(self, "Succès", "Les désinstallations ont été lancées.")

        # Proposer nettoyage résidus pour chaque logiciel désinstallé
        for row in checked_indexes:
            sw = self.software_list[row]
            name = sw.get("name", "Inconnu")
            self.clean_residuals(name)

        # Rafraîchir la liste
        self.populate_list()


def main(self, comm):
    uninstaller_plugin = UninstallerPlugin(comm)
    self.setCentralWidget(uninstaller_plugin)
