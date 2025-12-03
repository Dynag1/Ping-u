# This Python file uses the following encoding: utf-8
import sys
import os
import subprocess
import signal
import time

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
    from PySide6.QtWidgets import QAbstractItemView, QMessageBox, QMenu
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QAction, QActionGroup
    from PySide6.QtCore import QObject, Signal, Qt, QPoint, QModelIndex, QTranslator, QEvent, QCoreApplication, QLocale, QSortFilterProxyModel
    from src.ui_mainwindow import Ui_MainWindow
    import qt_themes
    GUI_AVAILABLE = True
except ImportError:
    # Mode headless ou environnement sans GUI
    GUI_AVAILABLE = False
    qt_themes = None
    # Créer des classes factices pour éviter les erreurs d'import
    class QObject: pass
    class Signal: 
        def __init__(self, *args): pass
        def emit(self, *args): pass
        def connect(self, *args): pass
    class QMainWindow: pass
    class QSortFilterProxyModel: pass
    class QPoint: pass
    class QModelIndex: pass
    class QColor: pass
    class QAction: pass
    class QActionGroup: pass
    class QStandardItem:
        def __init__(self, text=""): 
            self._text = str(text) if text else ""
            self._background = None
            self._data = {}
        def text(self): return self._text
        def setText(self, text): self._text = str(text)
        def setBackground(self, color): self._background = color
        def background(self): return self._background
        def setData(self, data, role=0): self._data[role] = data
        def data(self, role=0): return self._data.get(role)
        def setEditable(self, editable): pass
    class QStandardItemModel:
        def __init__(self, *args):
            self._rows = []
            self._headers = []
            self._column_count = 0
        def rowCount(self): return len(self._rows)
        def columnCount(self): return self._column_count
        def appendRow(self, items):
            self._rows.append(items)
            if items and len(items) > self._column_count:
                self._column_count = len(items)
        def removeRows(self, start, count): 
            del self._rows[start:start+count]
        def removeRow(self, row): 
            if 0 <= row < len(self._rows):
                del self._rows[row]
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
        def index(self, row, col, parent=None):
            return QModelIndex()
        def data(self, index, role=0):
            return None
        def dataChanged(self):
            class FakeSignal:
                def connect(self, *args): pass
                def emit(self, *args): pass
            return FakeSignal()
        def rowsInserted(self):
            class FakeSignal:
                def connect(self, *args): pass
            return FakeSignal()
        def rowsRemoved(self):
            class FakeSignal:
                def connect(self, *args): pass
            return FakeSignal()
    class QEvent:
        LanguageChange = 0
    class Qt:
        DisplayRole = 0
        ItemIsEditable = 0
        BackgroundRole = 0
        UserRole = 0
    class Ui_MainWindow: pass

from src import var, fct, lic, threadAjIp, db, sFenetre
from src import fctXls, fctMaj
import src.Snyf.main as snyf
from src.controllers.settings_controller import SettingsController
from src.controllers.main_controller import MainController
from src.web_server import WebServer
import threading
import webbrowser
import importlib
import platform



from src.utils.logger import setup_logging, get_logger
from src.utils.colors import AppColors

# Initialisation du logging
setup_logging()
logger = get_logger(__name__)

# Suppression de la redirection stdout/stderr obsolète
# sys.stdout = open('logs/stdout.log', 'w')
# sys.stderr = open('logs/stderr.log', 'w')

class IPSortProxyModel(QSortFilterProxyModel):
    """Proxy model pour trier les IP numériquement"""
    def lessThan(self, left, right):
        # Récupérer les colonnes
        left_col = left.column()
        right_col = right.column()
        
        # Pour la colonne IP (colonne 1), trier numériquement
        if left_col == 1 or right_col == 1:
            left_data = self.sourceModel().data(left, Qt.DisplayRole)
            right_data = self.sourceModel().data(right, Qt.DisplayRole)
            
            if left_data and right_data:
                try:
                    # Convertir IP en tuple d'entiers pour tri numérique
                    left_parts = [int(x) for x in str(left_data).split('.')]
                    right_parts = [int(x) for x in str(right_data).split('.')]
                    return left_parts < right_parts
                except:
                    pass
        
        # Pour les autres colonnes, tri par défaut
        return super().lessThan(left, right)

class Communicate(QObject):
    addRow = Signal(str, str, str, str, str, str, bool)
    progress = Signal(int)
    start_monitoring_signal = Signal()
    stop_monitoring_signal = Signal()
    relaodWindow = Signal(bool)


class MainWindow(QMainWindow):
    popup_signal = Signal(str)
    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def closeEvent(self, event):
        """Fermeture propre de l'application"""
        logger.info("Fermeture de l'application demandée")
        self.cleanup_resources()
        event.accept()

    def cleanup_resources(self):
        """Nettoyage propre de toutes les ressources"""
        # Éviter la double exécution (par exemple via menu Quitter + closeEvent)
        if getattr(self, '_is_cleaning_up', False):
            return
        self._is_cleaning_up = True
        
        try:
            # 1. Arrêter le flag global
            var.tourne = False
            
            # 2. Arrêter le monitoring via le contrôleur
            if hasattr(self, 'main_controller') and self.main_controller:
                self.main_controller.stop_monitoring()
                # Traiter les événements Qt pour laisser le temps aux threads de se terminer
                from PySide6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
            
            # 3. Arrêter le serveur web
            if hasattr(self, 'web_server') and self.web_server:
                logger.info("Arrêt du serveur web lors de la fermeture")
                self.web_server.stop()
                self.web_server = None
            
            # 4. Sauvegarder les paramètres
            try:
                db.save_param_db()
                logger.info("Paramètres sauvegardés")
            except Exception as e:
                logger.error(f"Erreur sauvegarde paramètres: {e}", exc_info=True)

            # 4b. Sauvegarde automatique de la liste de suivi
            try:
                if not os.path.exists("bd"):
                    os.makedirs("bd", exist_ok=True)
                autosave_path = os.path.join("bd", "autosave.pin")
                if self.treeIpModel.rowCount() > 0:
                    fct.save_csv(self, self.treeIpModel, filepath=autosave_path, silent=True)
                    logger.info(f"Liste de suivi sauvegardée automatiquement dans {autosave_path} ({self.treeIpModel.rowCount()} hôtes)")
                else:
                    logger.warning("Aucun hôte à sauvegarder pour l'autosave")
            except Exception as e:
                logger.error(f"Erreur sauvegarde automatique liste: {e}", exc_info=True)
                
            # 5. Traiter les derniers événements Qt
            QCoreApplication.processEvents()
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}", exc_info=True)

    def __init__(self):

        super().__init__()
        self.translators = []
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.translator = QTranslator()
        result = db.lire_param_gene()
        if not result or len(result) < 3:
            logger.warning("Paramètres généraux manquants, utilisation du thème par défaut.")
            result = ["", "", "nord"]
        self.change_theme(result[2])
        self.create_language_menu()
        self.comm = Communicate()
        self.tree_view = self.ui.treeIp
        
        # Contrôleurs
        self.settings_controller = SettingsController(self)
        self.main_controller = MainController(self)
        
        # Serveur Web
        self.web_server = None
        self.web_server_running = False
        
        self.load_language(QLocale().name()[:2])
        
        # Initialisation de l'application
        self._initialize_app()

    def _initialize_app(self):
        """Initialisation complète de l'application"""
        if lic.verify_license() == False:
            self.ui.checkMail.setEnabled(False)
            self.ui.checkDbExterne.setEnabled(False)
            self.ui.checkTelegram.setEnabled(False)
            self.ui.checkMailRecap.setEnabled(False)
            
        os.makedirs("cle", exist_ok=True)
        
        # Connexion des signaux
        self._setup_connections()
        
        # Chargement des plugins
        #self.plugin = fct.plug(self)
        #self.menuPlugin(self.plugin)
        
        self.ui.progressBar.hide()
        lic.verify_license()
        
        # Initialisation de l'arbre
        self.tree_view = self.ui.treeIp
        self.treeIpHeader(self.tree_view)
        # IP locale
        self.ui.txtIp.setText(fct.getIp(self))

        # Chargement automatique de la dernière liste de suivi
        try:
            autosave_path = os.path.join("bd", "autosave.pin")
            loaded = False
            
            if os.path.exists(autosave_path):
                logger.info(f"Chargement de la liste automatique: {autosave_path}")
                fct.load_csv(self, self.treeIpModel, autosave_path)
                if self.treeIpModel.rowCount() > 0:
                    loaded = True
            
            if not loaded and os.path.exists('bd'):
                files = [f for f in os.listdir('bd') if f.endswith('.pin') and f != 'autosave.pin']
                if files:
                    latest_file = max([os.path.join('bd', f) for f in files], key=os.path.getmtime)
                    logger.info(f"Chargement du dernier fichier (fallback): {latest_file}")
                    fct.load_csv(self, self.treeIpModel, latest_file)
        except Exception as e:
            logger.error(f"Erreur chargement automatique liste: {e}", exc_info=True)
        
        # Chargement des paramètres UI
        # Chargement des paramètres UI
        self.settings_controller.load_ui_settings()
        
        # Initialisation de la couleur du bouton Start
        self.ui.butStart.setStyleSheet(f"background-color: {var.couleur_vert}; color: black;")
        self.ui.butStart.setText("Start")

    def _setup_connections(self):
        """Configuration des connexions signaux/slots"""
        self.ui.butIp.clicked.connect(self.butIpClic)
        self.ui.butStart.clicked.connect(self.butStart)
        self.ui.menuClose.triggered.connect(self.close)
        #self.ui.actionG_rer.triggered.connect(self.plugGerer)
        self.ui.actionMaj.triggered.connect(lambda: fctMaj.main(self))
        # Modele alertes
        self.ui.spinDelais.valueChanged.connect(self.on_spin_delais_changed)
        self.ui.spinHs.valueChanged.connect(self.on_spin_spinHs_changed)
        self.ui.checkPopup.clicked.connect(self.popup)
        self.ui.checkMail.clicked.connect(self.mail)
        self.ui.checkTelegram.clicked.connect(self.telegram)
        self.ui.checkMailRecap.clicked.connect(self.mailRecap)
        self.ui.checkDbExterne.clicked.connect(self.pingDb)
        # Fentres
        self.ui.checkDbExterne.clicked.connect(self.pingDb)
        # Fentres
        self.ui.actionSauvegarder_les_r_glages.triggered.connect(self.settings_controller.save_settings)
        self.ui.actionEnvoies.triggered.connect(sFenetre.fenetreParamEnvoie)
        self.ui.actionMail_recap.triggered.connect(sFenetre.fenetreMailRecap)
        self.ui.actionG_n_raux.triggered.connect(lambda: sFenetre.fenetreParametre(self, self.comm))
        self.ui.actionAPropos.triggered.connect(sFenetre.fenAPropos)

        # Fonction Save et Load
        self.ui.actionSauvegarder.triggered.connect(lambda: fct.save_csv(self, self.treeIpModel))
        self.ui.actionOuvrir.triggered.connect(lambda: fct.load_csv(self, self.treeIpModel))
        self.ui.actionTout_effacer.triggered.connect(lambda: fct.clear(self, self.treeIpModel))
        # Fonction export excel
        self.ui.actionExporter_xls.triggered.connect(lambda: fctXls.saveExcel(self, self.treeIpModel))
        
        # Signaux pour l'API web (thread-safe)
        self.comm.start_monitoring_signal.connect(self.main_controller.start_monitoring)
        self.comm.stop_monitoring_signal.connect(self.main_controller.stop_monitoring)
        self.ui.actionImporter_xls.triggered.connect(lambda: fctXls.openExcel(self, self.treeIpModel))
        self.ui.actionSnyf_2.triggered.connect(lambda: snyf.main(self, self.comm))
        self.ui.actionCleGpg.triggered.connect(lambda: self.pgp())
        # Communication
        self.comm.relaodWindow.connect(self.reload_main_window)
        self.comm.addRow.connect(self.on_add_row)
        self.comm.progress.connect(self.barProgress)
        self.popup_signal.connect(self.show_popup)
        self.ui.actionNotice.triggered.connect(lambda: self.notice())
        # Logs
        self.ui.actionLogs.triggered.connect(self.open_logs)
        self.ui.actionEffacer_logs.triggered.connect(self.clear_logs)
        
        # Menu Serveur Web
        self._setup_web_server_menu()
        
        # Connexion des signaux du modèle pour détecter les changements
        self.treeIpModel.dataChanged.connect(self.on_treeview_data_changed)
        self.treeIpModel.rowsInserted.connect(self.on_treeview_rows_inserted)
        self.treeIpModel.rowsRemoved.connect(self.on_treeview_rows_removed)

    def change_theme(self, theme_name):
        if qt_themes is None:
            return
        try:
            qt_themes.set_theme(theme_name)
        except:
            qt_themes.set_theme("nord")

    def show_popup(self, mess):
          QMessageBox.information(self, self.tr("Alerte"), mess)

# Language
## Path du langage ##
    def get_language_path(self):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        return os.path.join(base_path, 'src', 'languages')


## Charger le langage ##
    def load_language(self, lang_code):
        language_dir = self.get_language_path()
        app = QApplication.instance()
        if hasattr(self, 'translator') and self.translator is not None:
            for translator in self.translators:
                app.removeTranslator(translator)
            self.translators.clear()
        self.translator = QTranslator()
        if self.translator.load(f"{self.get_language_path()}/app_{lang_code}.qm"):
            app.installTranslator(self.translator)
            self.translators.append(self.translator)
        self.retranslateUi()

## Créer UI ##
    def retranslateUi(self):
        # Réinitialise toute l'interface
        _translate = QCoreApplication.translate
        self.ui.retranslateUi(self)  # Si vous utilisez un UI chargé
        self.langReload()

## Menu Language ##
    def create_language_menu(self):
        lang_group = QActionGroup(self)
        lang_group.triggered[QAction].connect(self.change_language)

        lang_group.setExclusive(True)
        self.ui.menuLangue.clear()
        for lang_file in os.listdir(self.get_language_path()):
            if lang_file.startswith("app_") and lang_file.endswith(".qm"):
                lang_code = lang_file[4:-3]  # 'app_fr.qm' -> 'fr'
                action = QAction(QLocale(lang_code).nativeLanguageName().capitalize(), self)
                action.setData(lang_code)
                action.setCheckable(True)
                if lang_code == QLocale().name()[:2]:
                    action.setChecked(True)
                lang_group.addAction(action)
                self.ui.menuLangue.addAction(action)

## Changement de langue ##
    def change_language(self, action):
        lang_code = action.data()
        self.load_language(lang_code)
        self.retranslateUi()

## Rechager l'UI ##
    def langReload(self):
        # print("lang")
        self.ui.labVersion1.setText(self.tr("Ping ü version : ")+var.version)
        textLiNok = self.tr("Vous n'avez pas de license active")
        if lic.verify_license():
            licActive = lic.jours_restants_licence()
            self.ui.labLic.setText(QCoreApplication.translate("MainWindow", "Votre license est active pendant ")+licActive+self.tr(" jours"))
        else:
            self.ui.labLic.setText(textLiNok)
        self.treeIpHeader(self.tree_view)
        self.ui.txtAlive.clear()
        self.ui.txtAlive.addItem(self.tr("Alive"))
        self.ui.txtAlive.addItem(self.tr("Tout"))
        self.ui.txtAlive.addItem(self.tr("Site"))
        
        # Mise à jour du menu serveur web
        self._update_web_server_menu_text()


# Plugin #
## Menu des plugins ##
    def menuPlugin(self, plugin):
        try:
            for plug in plugin:
                #self.ui.menuPlugin.addMenu(plug)
                action_directe = QAction(plug, self)
                action_directe.triggered.connect(lambda checked=False, p=plug: self.pluginLance(p))
                # Ajout direct de l'action dans le menu (PAS dans un sous-menu)
                self.ui.menuPlugin.addAction(action_directe)
        except Exception as e:
            logger.error(f"Erreur menu plugin: {e}", exc_info=True)
            QMessageBox.information(
                self,
                "Erreur",
                str(e),
                QMessageBox.Ok
            )

## Chargement des plugins ##
    def pluginLance(self, plug):
        path = os.path.abspath(os.getcwd())
        try:
            sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), ".")))  # Adaptez selon votre structure

            module_name = f"fichier.plugin.{plug}.main"
            plugin_module = importlib.import_module(module_name)
            if hasattr(plugin_module, "main"):
                plugin_module.main(self, self.comm)
            else:
                print(f"Le plugin '{plug}' n'a pas de fonction 'run'.")
        except Exception as e:
            logger.error(f"Erreur lancement plugin {plug}: {e}", exc_info=True)
            QMessageBox.information(
                self,
                "Erreur",
                f"fichier.plugin.{plug}.main"+" - -"+str(e),
                QMessageBox.Ok
            )

    def plugGerer(self):
        try:
            import os
            import subprocess
            path = os.path.abspath(os.getcwd())+"\\fichier\\plugin"
            FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
            path = os.path.normpath(path)
            if os.path.isdir(path):
                subprocess.run([FILEBROWSER_PATH, path])
            elif os.path.isfile(path):
                subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])
        except Exception as e:
            logger.error(f"Erreur gestion plugin: {e}", exc_info=True)


    def popup(self):
        if self.ui.checkPopup.isChecked():
            var.popup = True
        else:
            var.popup = False

    def mail(self):
        if self.ui.checkMail.isChecked():
            var.mail = True
        else:
            var.mail = False

    def telegram(self):
        if self.ui.checkTelegram.isChecked():
            var.telegram = True
        else:
            var.telegram = False

    def mailRecap(self):
        if self.ui.checkMailRecap.isChecked():
            var.mailRecap = True
        else:
            var.mailRecap = False

    def pingDb(self):
        if self.ui.checkDbExterne.isChecked():
            var.dbExterne = True
        else:
            var.dbExterne = False

    def close(self):
        self.cleanup_resources()
        QApplication.quit()

    def treeIpHeader(self, tree_view):
        self.tree_view = self.ui.treeIp
        
        # Créer le modèle seulement s'il n'existe pas déjà
        if not hasattr(self, 'treeIpModel') or self.treeIpModel is None:
            self.treeIpModel = QStandardItemModel()
            self.proxyModel = IPSortProxyModel()
            self.proxyModel.setSourceModel(self.treeIpModel)
            self.tree_view.setModel(self.proxyModel)
            
        # Toujours mettre à jour les en-têtes (pour la traduction)
        self.treeIpModel.setHorizontalHeaderLabels([
            self.tr("Id"), self.tr("IP"), self.tr("Nom"), self.tr("Mac"), 
            self.tr("Port"), self.tr("Latence"), self.tr("Temp"), self.tr("Suivi"), 
            self.tr("Comm"), self.tr("Excl")
        ])
        
        self.tree_view.setSortingEnabled(True)
        header = self.tree_view.header()
        header.setStretchLastSection(False)
        for i in range(self.treeIpModel.columnCount()):
            if i in [0, 5, 6, 7, 9]:  # Colonnes figées (Id, Latence, Temp, Suivi, Excl)
                header.setSectionResizeMode(i, QHeaderView.Fixed)
            else:  # Colonnes étirables
                header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.tree_view.setColumnWidth(0, 1)
        self.tree_view.setColumnWidth(5, 50)  # Latence
        self.tree_view.setColumnWidth(6, 50)  # Temp
        self.tree_view.setColumnWidth(7, 50)  # Suivi
        self.tree_view.setColumnWidth(9, 50)  # Excl
        self.tree_view.setStyleSheet("QTreeView, QTreeView::item { color: black; }")
        self.tree_view.setSelectionMode(QAbstractItemView.NoSelection)

        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        # Déconnecter l'ancien signal pour éviter les doublons si on repasse ici
        try:
            self.tree_view.customContextMenuRequested.disconnect()
        except:
            pass
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.tree_view.header().setSortIndicator(1, Qt.AscendingOrder)

    def show_context_menu(self, pos: QPoint):
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return

        menu = QMenu()
        action_web = QAction(self.tr("Ouvrir dans le navigateur"), self)
        action_suppr = QAction(self.tr("Supprimer"), self)
        action_excl = QAction(self.tr("Exclure"), self)
        action_web.triggered.connect(lambda: self.handle_web_action(index))
        action_suppr.triggered.connect(lambda: self.find_and_remove(index))
        action_excl.triggered.connect(lambda: self.ipExcl(index))
        menu.addAction(action_web)
        menu.addAction(action_suppr)
        menu.addAction(action_excl)
        menu.exec(self.tree_view.viewport().mapToGlobal(pos))

    def handle_web_action(self, index: QModelIndex):
        ip_item = self.treeIpModel.item(index.row(), 1)
        webbrowser.open('http://' + ip_item.text())
        logger.info(f"Ouverture navigateur pour {ip_item.text()}")

    def find_and_remove(self, index: QModelIndex):
        self.treeIpModel.removeRow(index.row())

    def ipExcl(self, index: QModelIndex):
        x_item = QStandardItem("x")
        self.treeIpModel.setItem(index.row(), 8, x_item)


    def butIpClic(self):
        ip = self.ui.txtIp.text()
        nbr_hote = self.ui.spinHote.value()
        alive = self.ui.txtAlive.currentText()
        port = self.ui.txtPort.text()
        self.ui.progressBar.show()
        threading.Thread(target=threadAjIp.main, args=(self, self.comm, self.treeIpModel, ip,nbr_hote, alive, port, "")).start()

    def on_add_row(self, i, ip, nom, mac, port, extra, is_ok):
        items = [
            QStandardItem(i),         # 0: Id
            QStandardItem(ip),        # 1: IP
            QStandardItem(nom),       # 2: Nom
            QStandardItem(mac),       # 3: Mac
            QStandardItem(str(port)), # 4: Port
            QStandardItem(extra),     # 5: Latence
            QStandardItem(""),        # 6: Temp (sera remplie par SNMP)
            QStandardItem(""),        # 7: Suivi
            QStandardItem(""),        # 8: Comm
            QStandardItem("")         # 9: Excl
        ]
        # Rendre certaines colonnes non éditables
        for col in [0, 1, 3, 5, 6, 7, 9]:  # Id, IP, Mac, Latence, Temp, Suivi, Excl
            items[col].setFlags(items[col].flags() & ~Qt.ItemIsEditable)

        # Coloration selon is_ok : vert clair pour IP OK, rouge pour IP DOWN
        couleur = QColor(AppColors.VERT_PALE) if is_ok else QColor(AppColors.ROUGE_PALE)
        for item in items:
            item.setBackground(couleur)

        self.treeIpModel.appendRow(items)

    def butStart(self):
        self.main_controller.toggle_monitoring()

    def on_spin_delais_changed(self, value):
        var.delais = value
        if value < 60:
            valueA = str(value)+" s"
            valueB = ""
        elif value < 3600:
            valueA = value//60
            valueB = value % 60
            valueB = f"{int(valueB):02d}"
            valueA = str(valueA)+" m "+str(valueB)
        else:
            valueA = value//3600
            valueB = (value % 3600) // 60
            valueA = str(valueA)+" h "+f"{int(valueB):02d}"

        self.ui.labDelaisH.setText(str(valueA))

    def on_spin_spinHs_changed(self, value):
        old_value = var.nbrHs
        var.nbrHs = value
        
        # Si le monitoring est actif et que la valeur a changé, nettoyer les listes
        if old_value != value and hasattr(self, 'main_controller') and self.main_controller:
            if self.main_controller.ping_manager is not None:
                # Nettoyer les listes d'alertes pour éviter les fausses alertes
                self._clean_alert_lists_for_new_threshold(value)
                logger.info(f"Seuil nbrHs modifié de {old_value} à {value} pendant le monitoring")
    
    def _clean_alert_lists_for_new_threshold(self, new_threshold):
        """
        Nettoie les listes d'alertes pour s'adapter au nouveau seuil.
        Si un compteur dépasse le nouveau seuil, il est ramené au nouveau seuil - 1.
        """
        try:
            # Fonction pour nettoyer une liste
            def clean_list(liste, list_name):
                cleaned_count = 0
                for ip, count in list(liste.items()):
                    count_int = int(count)
                    # Les états spéciaux (10 = alerte envoyée, 20 = retour OK) ne doivent jamais être modifiés
                    if count_int >= 10:
                        continue
                    # Si le compteur dépasse ou égale le nouveau seuil, on le limite
                    if count_int >= new_threshold:
                        liste[ip] = max(1, new_threshold - 1)
                        cleaned_count += 1
                return cleaned_count
            
            hs_cleaned = clean_list(var.liste_hs, "liste_hs")
            mail_cleaned = clean_list(var.liste_mail, "liste_mail")
            telegram_cleaned = clean_list(var.liste_telegram, "liste_telegram")
            
            total_cleaned = hs_cleaned + mail_cleaned + telegram_cleaned
            if total_cleaned > 0:
                logger.info(f"Nettoyage des listes d'alertes: {hs_cleaned} HS, {mail_cleaned} mail, {telegram_cleaned} telegram")
                
        except Exception as e:
            logger.error(f"Erreur nettoyage listes alertes: {e}", exc_info=True)

    def barProgress(self, i):
        self.ui.progressBar.setValue(i)
        if i == 100:
            self.ui.progressBar.hide()
            QMessageBox.information(
                self,
                self.tr("Succès"),
                self.tr("Scan terminé, ")+str(var.u)+self.tr(" hôtes trouvés"),
                QMessageBox.Ok
            )

    def reload_main_window(bool):
        global window
        window.hide()
        window.deleteLater()
        window = MainWindow()
        window.show()

    def pgp(self):
        systeme = platform.system()
        
        # GPG n'est pas disponible sur Linux dans cette application
        if systeme == "Linux":
            QMessageBox.warning(
                self,
                self.tr("GPG non disponible"),
                self.tr("La fonctionnalité GPG n'est pas disponible sur Linux.\nLes emails seront envoyés en clair."),
                QMessageBox.Ok
            )
            return
        
        chemin = os.path.abspath("cle")
        if not os.path.exists(chemin):
            os.makedirs(chemin, exist_ok=True)
        
        if systeme == "Windows":
            os.startfile(chemin)
        elif systeme == "Darwin":
            subprocess.run(["open", chemin])
        else:
            subprocess.run(["xdg-open", chemin])

    def notice(self):
        webbrowser.open("https://github.com/Dynag1/Ping-u/blob/main/Notice.md")

    def open_logs(self):
        """Ouvre le fichier de logs dans l'éditeur par défaut."""
        import os
        log_file = os.path.abspath("logs/app.log")
        if os.path.exists(log_file):
            try:
                os.startfile(log_file)  # Windows
            except AttributeError:
                # Linux/Mac
                import subprocess
                subprocess.call(['xdg-open', log_file])
        else:
            QMessageBox.warning(self, self.tr("Logs"), self.tr("Le fichier de logs n'existe pas encore."))

    def clear_logs(self):
        """Efface le contenu du fichier de logs."""
        import os
        log_file = os.path.abspath("logs/app.log")
        try:
            if os.path.exists(log_file):
                with open(log_file, 'w') as f:
                    f.write('')
                logger.info("Logs effacés par l'utilisateur")
                QMessageBox.information(self, self.tr("Succès"), self.tr("Les logs ont été effacés."))
            else:
                QMessageBox.warning(self, self.tr("Logs"), self.tr("Le fichier de logs n'existe pas."))
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement des logs: {e}", exc_info=True)
            msg = self.tr("Impossible d'effacer les logs")
            QMessageBox.critical(self, self.tr("Erreur"), f"{msg}: {e}")
    
    # ============= Serveur Web =============
    
    def _setup_web_server_menu(self):
        """Crée le sous-menu Serveur Web dans le menu Fonction"""
        try:
            # Créer un sous-menu "Serveur Web" dans le menu "Fonction"
            self.web_menu = QMenu(self.tr("Serveur Web"), self)
            
            self.action_toggle_web_server = QAction(self.tr("Démarrer le serveur"), self)
            self.action_toggle_web_server.triggered.connect(self.toggle_web_server)
            self.web_menu.addAction(self.action_toggle_web_server)
            
            self.action_open_web_page = QAction(self.tr("Ouvrir dans le navigateur"), self)
            self.action_open_web_page.triggered.connect(self.open_web_page)
            self.action_open_web_page.setEnabled(False)
            self.web_menu.addAction(self.action_open_web_page)
            
            self.action_show_web_urls = QAction(self.tr("Voir les URLs d'accès"), self)
            self.action_show_web_urls.triggered.connect(self.show_web_urls)
            self.action_show_web_urls.setEnabled(False)
            self.web_menu.addAction(self.action_show_web_urls)
            
            # Ajouter le sous-menu au menu "Fonction"
            self.ui.menuFonctions.addSeparator()
            self.ui.menuFonctions.addMenu(self.web_menu)
            
        except Exception as e:
            logger.error(f"Erreur création menu serveur web: {e}", exc_info=True)
    
    def _update_web_server_menu_text(self):
        """Met à jour les textes du menu serveur web lors du changement de langue"""
        try:
            if hasattr(self, 'web_menu'):
                self.web_menu.setTitle(self.tr("Serveur Web"))
            
            if hasattr(self, 'action_toggle_web_server'):
                # Déterminer le texte en fonction de l'état du serveur
                if self.web_server_running:
                    self.action_toggle_web_server.setText(self.tr("Arrêter le serveur"))
                else:
                    self.action_toggle_web_server.setText(self.tr("Démarrer le serveur"))
            
            if hasattr(self, 'action_open_web_page'):
                self.action_open_web_page.setText(self.tr("Ouvrir dans le navigateur"))
            
            if hasattr(self, 'action_show_web_urls'):
                self.action_show_web_urls.setText(self.tr("Voir les URLs d'accès"))
                
        except Exception as e:
            logger.error(f"Erreur mise à jour textes menu serveur web: {e}", exc_info=True)
    
    def toggle_web_server(self):
        """Démarre ou arrête le serveur web"""
        try:
            if not self.web_server_running:
                self.web_server = WebServer(self, port=9090)
                if self.web_server.start():
                    self.web_server_running = True
                    self.action_toggle_web_server.setText(self.tr("Arrêter le serveur"))
                    self.action_open_web_page.setEnabled(True)
                    self.action_show_web_urls.setEnabled(True)
                    
                    urls = self.web_server.get_access_urls()
                    msg = self.tr("Serveur web démarré avec succès !\n\n")
                    msg += self.tr("Accès local: ") + urls['local'] + "\n"
                    msg += self.tr("Accès réseau: ") + urls['network']
                    QMessageBox.information(self, self.tr("Serveur Web"), msg)
                    logger.info("Serveur web démarré")
                else:
                    QMessageBox.critical(self, self.tr("Erreur"), 
                                       self.tr("Impossible de démarrer le serveur web.\nLe port 9090 est peut-être déjà utilisé."))
            else:
                if self.web_server:
                    self.web_server.stop()
                    self.web_server = None
                self.web_server_running = False
                self.action_toggle_web_server.setText(self.tr("Démarrer le serveur"))
                self.action_open_web_page.setEnabled(False)
                self.action_show_web_urls.setEnabled(False)
                QMessageBox.information(self, self.tr("Serveur Web"), 
                                      self.tr("Serveur web arrêté"))
                logger.info("Serveur web arrêté")
                
        except Exception as e:
            logger.error(f"Erreur toggle serveur web: {e}", exc_info=True)
            QMessageBox.critical(self, self.tr("Erreur"), 
                               self.tr("Erreur lors du démarrage/arrêt du serveur: ") + str(e))
    
    def open_web_page(self):
        """Ouvre la page web dans le navigateur par défaut"""
        if self.web_server_running and self.web_server:
            try:
                urls = self.web_server.get_access_urls()
                webbrowser.open(urls['local'])
                logger.info(f"Ouverture page web: {urls['local']}")
            except Exception as e:
                logger.error(f"Erreur ouverture page web: {e}", exc_info=True)
    
    def show_web_urls(self):
        """Affiche les URLs d'accès au serveur web"""
        if self.web_server_running and self.web_server:
            try:
                urls = self.web_server.get_access_urls()
                msg = self.tr("URLs d'accès au serveur web:\n\n")
                msg += self.tr("Accès local (sur cet ordinateur):\n")
                msg += urls['local'] + "\n\n"
                msg += self.tr("Accès réseau (depuis un autre PC):\n")
                msg += urls['network'] + "\n\n"
                msg += self.tr("Note: Assurez-vous que le pare-feu autorise les connexions sur le port 9090.")
                QMessageBox.information(self, self.tr("URLs d'accès"), msg)
            except Exception as e:
                logger.error(f"Erreur affichage URLs: {e}", exc_info=True)
    
    def on_treeview_data_changed(self, topLeft, bottomRight, roles):
        """Appelé quand des données du treeview changent"""
        if self.web_server_running and self.web_server:
            self.web_server.broadcast_update()
    
    def on_treeview_rows_inserted(self, parent, first, last):
        """Appelé quand des lignes sont ajoutées au treeview"""
        if self.web_server_running and self.web_server:
            self.web_server.broadcast_update()
    
    def on_treeview_rows_removed(self, parent, first, last):
        """Appelé quand des lignes sont supprimées du treeview"""
        if self.web_server_running and self.web_server:
            self.web_server.broadcast_update()


def run_headless_mode():
    """Mode headless sans interface graphique (pour serveurs Linux)"""
    import argparse
    import signal
    import time
    from flask import Flask
    
    logger.info("[HEADLESS] Demarrage en mode headless (sans interface graphique)")
    
    # Créer le fichier PID
    pid_file = 'pingu_headless.pid'
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    logger.info(f"PID: {os.getpid()} (fichier: {pid_file})")
    
    # Initialiser la base de données et les paramètres
    try:
        # Paramètres généraux
        result_gene = db.lire_param_gene()
        if not result_gene or len(result_gene) < 3:
            logger.warning("Paramètres généraux manquants, utilisation des valeurs par défaut.")
        else:
            db.nom_site() # Charge nom_site et license dans var
            
        # Paramètres alertes et délais
        result_db = db.lire_param_db()
        if result_db and len(result_db) >= 7:
            from src import var
            var.delais = result_db[0]
            try:
                var.nbrHs = int(result_db[1])
            except (ValueError, TypeError):
                var.nbrHs = 3
                logger.warning(f"Valeur invalide pour nbrHs ({result_db[1]}), utilisation de la valeur par défaut: 3")
            
            var.popup = result_db[2]
            var.mail = result_db[3]
            var.telegram = result_db[4]
            var.mailRecap = result_db[5]
            var.dbExterne = result_db[6]
            logger.info(f"Paramètres chargés: Délai={var.delais}s, Mail={var.mail}, Telegram={var.telegram}, Popup={var.popup}")
        else:
            logger.warning("Paramètres d'alertes manquants ou incomplets")
            
    except Exception as e:
        logger.warning(f"Erreur chargement paramètres: {e}")
    
    # Créer une application Qt minimale (nécessaire pour QStandardItemModel)
    if GUI_AVAILABLE:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
    else:
        # En mode headless pur sans PySide6, on crée un objet dummy
        # qui doit avoir une méthode exec() pour la boucle principale
        class DummyApp:
            def __init__(self):
                self._running = True
            def exec(self):
                while self._running:
                    time.sleep(1)
                return 0
            def quit(self):
                self._running = False
        app = DummyApp()
    
    # Créer un modèle de données minimal
    if GUI_AVAILABLE:
        from PySide6.QtGui import QStandardItemModel
    else:
        # Modèle minimal pour headless
        class QStandardItemModel:
            def __init__(self):
                self._rows = []
                self._headers = []
            def rowCount(self, parent=None): return len(self._rows)
            def columnCount(self, parent=None): return 10
            def setHorizontalHeaderLabels(self, labels): self._headers = labels
            def appendRow(self, items): self._rows.append(items)
            def removeRow(self, row): 
                if 0 <= row < len(self._rows):
                    self._rows.pop(row)
            def removeRows(self, row, count):
                if 0 <= row < len(self._rows):
                    del self._rows[row:row+count]
            def item(self, row, col):
                if 0 <= row < len(self._rows) and 0 <= col < len(self._rows[row]):
                    return self._rows[row][col]
                return None
            def setItem(self, row, col, item):
                if 0 <= row < len(self._rows):
                    while len(self._rows[row]) <= col:
                        self._rows[row].append(None)
                    self._rows[row][col] = item
            def index(self, row, col):
                # Retourne un objet simple qui peut stocker row/col
                class Index:
                    def __init__(self, r, c, m): self._r, self._c, self._m = r, c, m
                    def data(self, role=None): 
                        item = self._m.item(self._r, self._c)
                        return item.text() if item else ""
                return Index(row, col, self)
            def data(self, index, role=None):
                return index.data(role)

    treeIpModel = QStandardItemModel()
    treeIpModel.setHorizontalHeaderLabels([
        "Id", "IP", "Nom", "Mac", "Port", "Latence", "Temp", "Suivi", "Comm", "Excl"
    ])
    
    # Créer une fenêtre "virtuelle" pour le serveur web
    class HeadlessWindow:
        def __init__(self):
            self.treeIpModel = treeIpModel
            self.comm = Communicate()
            self.web_server = None
            self.web_server_running = False
            
            # Pseudo UI pour compatibilité (DOIT être créé AVANT MainController)
            class PseudoUI:
                class PseudoButton:
                    def __init__(self):
                        self._checked = False
                    
                    def isChecked(self):
                        return self._checked
                    
                    def setChecked(self, value):
                        self._checked = value
                    
                    def setStyleSheet(self, style):
                        pass
                    
                    def setText(self, text):
                        logger.info(f"Status: {text}")
                
                def __init__(self):
                    self.butStart = self.PseudoButton()
            
            self.ui = PseudoUI()
            
            # Créer le contrôleur APRÈS self.ui
            self.main_controller = MainController(self)
        
        def tr(self, text):
            """Traduction minimale pour compatibilité Qt"""
            return text
        
        def show_popup(self, message):
            """Afficher popup - mode headless log seulement"""
            logger.info(f"[POPUP] {message}")
            # Envoyer la notification au client web si possible
            if self.web_server and self.web_server.socketio:
                try:
                    self.web_server.socketio.emit('notification', {'message': message, 'type': 'warning'}, namespace='/')
                except Exception as e:
                    logger.error(f"Erreur envoi notification web: {e}")
            
        def on_add_row(self, i, ip, nom, mac, port, extra, is_ok):
            """Ajoute une ligne au modèle (appelé par le thread de scan)"""
            if GUI_AVAILABLE:
                from PySide6.QtGui import QStandardItem
            else:
                # Version Headless
                class QStandardItem:
                    def __init__(self, text=""): self._text = text
                    def text(self): return self._text
            
            items = [
                QStandardItem(str(i)),    # 0: Id
                QStandardItem(ip),        # 1: IP
                QStandardItem(nom),       # 2: Nom
                QStandardItem(mac),       # 3: Mac
                QStandardItem(str(port)), # 4: Port
                QStandardItem(extra),     # 5: Latence
                QStandardItem(""),        # 6: Temp
                QStandardItem(""),        # 7: Suivi
                QStandardItem(""),        # 8: Comm
                QStandardItem("")         # 9: Excl
            ]
            self.treeIpModel.appendRow(items)
            logger.info(f"Hôte ajouté: {ip} ({nom})")
            # Diffuser la mise à jour aux clients web
            if self.web_server:
                self.web_server.broadcast_update()
    
    window = HeadlessWindow()
    
    # Connecter les signaux
    window.comm.start_monitoring_signal.connect(window.main_controller.start_monitoring)
    window.comm.stop_monitoring_signal.connect(window.main_controller.stop_monitoring)
    window.comm.addRow.connect(window.on_add_row)
    
    # Charger les données existantes si disponibles
    hosts_loaded = False
    try:
        autosave_path = os.path.join("bd", "autosave.pin")
        if os.path.exists(autosave_path):
            logger.info(f"Chargement de la liste automatique: {autosave_path}")
            fct.load_csv(window, window.treeIpModel, autosave_path)
            hosts_loaded = window.treeIpModel.rowCount() > 0
        
        if not hosts_loaded and os.path.exists('bd'):
            files = [f for f in os.listdir('bd') if f.endswith('.pin') and f != 'autosave.pin']
            if files:
                latest_file = max([os.path.join('bd', f) for f in files], key=os.path.getmtime)
                logger.info(f"Chargement des données depuis {latest_file}")
                fct.load_csv(window, window.treeIpModel, latest_file)
                hosts_loaded = window.treeIpModel.rowCount() > 0
        
        if hosts_loaded:
            logger.info(f"{window.treeIpModel.rowCount()} hôte(s) chargé(s)")
    except Exception as e:
        logger.warning(f"Impossible de charger les données: {e}")
    
    # Démarrer le serveur web APRÈS le chargement des données
    from src.web_server import WebServer
    window.web_server = WebServer(window, port=9090)
    if window.web_server.start():
        window.web_server_running = True
        logger.info("[HEADLESS] Serveur web demarre sur http://0.0.0.0:9090")
    else:
        logger.error("[HEADLESS] Impossible de demarrer le serveur web")
        sys.exit(1)
    
    # Ne PAS démarrer le monitoring automatiquement
    # L'utilisateur peut le démarrer via l'interface web admin
    if hosts_loaded:
        logger.info(f"Monitoring pret pour {window.treeIpModel.rowCount()} hôte(s)")
        logger.info("Demarrez le monitoring via l'interface web: http://localhost:9090/admin")
    else:
        logger.info("Aucun hôte configuré. Configurez via l'interface web: http://localhost:9090/admin")
    
    # Gestionnaire de signal pour arrêt propre
    def signal_handler(signum, frame):
        logger.info(f"Signal {signum} reçu, arrêt de l'application...")
        cleanup_and_exit()
    
    def cleanup_and_exit():
        logger.info("[HEADLESS] Arret en cours...")
        
        # 1. Sauvegarde automatique de la liste de suivi (PRIORITÉ HAUTE)
        try:
            if not os.path.exists("bd"):
                os.makedirs("bd", exist_ok=True)
            autosave_path = os.path.join("bd", "autosave.pin")
            
            # Log explicite du nombre d'hôtes à sauvegarder
            if hasattr(window, 'treeIpModel'):
                row_count = window.treeIpModel.rowCount()
                logger.info(f"Tentative de sauvegarde automatique de {row_count} hôtes vers {autosave_path}")
            else:
                logger.warning("window.treeIpModel introuvable pour la sauvegarde")

            # Sauvegarde silencieuse pour éviter les popups en headless et erreur QObject parent
            fct.save_csv(window, window.treeIpModel, filepath=autosave_path, silent=True)
            
            if os.path.exists(autosave_path):
                size = os.path.getsize(autosave_path)
                logger.info(f"Liste de suivi sauvegardée automatiquement dans {autosave_path} (taille: {size} octets)")
            else:
                logger.error(f"Fichier {autosave_path} non trouvé après tentative de sauvegarde")
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde automatique liste: {e}", exc_info=True)
            
        # 2. Sauvegarder les paramètres
        try:
            db.save_param_db()
            logger.info("Paramètres sauvegardés")
        except Exception as e:
            logger.error(f"Erreur sauvegarde paramètres: {e}")

        # 3. Arrêter le monitoring
        try:
            if window.main_controller and window.main_controller.ping_manager:
                logger.info("Arrêt du monitoring...")
                window.main_controller.stop_monitoring()
                time.sleep(1)  # Attendre que le monitoring s'arrête
        except Exception as e:
            logger.error(f"Erreur arrêt monitoring: {e}")
            
        # 4. Arrêter le serveur web
        try:
            if window.web_server:
                logger.info("Arrêt du serveur web...")
                window.web_server.stop()
                time.sleep(2)  # Attendre que le serveur libère le port
        except Exception as e:
            logger.error(f"Erreur arrêt serveur web: {e}")
            
        # 5. Supprimer le fichier PID
        try:
            if os.path.exists(pid_file):
                os.remove(pid_file)
                logger.info("Fichier PID supprimé")
        except Exception as e:
            logger.error(f"Erreur suppression PID: {e}")
        
        # 6. Supprimer le fichier stop s'il existe
        try:
            if os.path.exists('pingu_headless.stop'):
                os.remove('pingu_headless.stop')
        except:
            pass
        
        logger.info("[HEADLESS] Arret termine proprement")
        
        # Force la fermeture
        os._exit(0)
    
    # Enregistrer les gestionnaires de signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("[HEADLESS] Application demarree en mode headless")
    logger.info("[HEADLESS] Pour arreter: python Pingu.py -stop")
    logger.info("[HEADLESS] Interface web admin: http://localhost:9090/admin")
    logger.info("   Identifiants par défaut: admin / a")
    
    # Gestionnaire pour la boucle principale
    def check_stop_file():
        if os.path.exists('pingu_headless.stop'):
            logger.info("Fichier stop détecté, arrêt de l'application...")
            os.remove('pingu_headless.stop')
            app.quit()
    
    # Timer pour vérifier le fichier stop toutes les secondes
    if GUI_AVAILABLE:
        from PySide6.QtCore import QTimer
        stop_check_timer = QTimer()
        stop_check_timer.timeout.connect(check_stop_file)
        stop_check_timer.start(1000)
    else:
        # En mode headless sans GUI, la boucle principale est dans app.exec() (DummyApp)
        # On doit modifier DummyApp pour vérifier le fichier stop
        # Note: On utilise une approche plus propre en surchargeant la méthode de l'instance
        original_exec = app.exec
        def looped_exec():
            while app._running:
                check_stop_file()
                time.sleep(1)
            return 0
        app.exec = looped_exec

    logger.info("[HEADLESS] Application demarree en mode headless")
    logger.info("[HEADLESS] Pour arreter: python Pingu.py -stop")
    logger.info("[HEADLESS] Interface web admin: http://localhost:9090/admin")
    logger.info("   Identifiants par défaut: admin / a")
    
    # Lancer la boucle d'événements Qt
    # C'est nécessaire pour que les signaux (start_monitoring) et les QThread fonctionnent
    exit_code = app.exec()
    
    # Nettoyage après la fin de la boucle
    cleanup_and_exit()
    sys.exit(exit_code)


def stop_headless_mode():
    """Arrête l'application en mode headless"""
    pid_file = 'pingu_headless.pid'
    
    if not os.path.exists(pid_file):
        print("❌ Aucune instance headless en cours d'exécution")
        print("💡 Si le port 9090 est toujours utilisé, exécutez:")
        print("   bash cleanup_raspberry.sh")
        return
    
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        print(f"🛑 Arrêt de l'application (PID: {pid})...")
        
        # Créer un fichier stop
        with open('pingu_headless.stop', 'w') as f:
            f.write('stop')
        
        # Attendre que l'application s'arrête
        import time
        for i in range(15):  # Augmenté à 15 secondes
            if not os.path.exists(pid_file):
                print("✅ Application arrêtée avec succès")
                # Nettoyer le fichier stop si l'application l'a pas fait
                if os.path.exists('pingu_headless.stop'):
                    try:
                        os.remove('pingu_headless.stop')
                    except:
                        pass
                # Attendre que le port soit libéré
                time.sleep(2)
                return
            time.sleep(1)
            if i % 3 == 0:
                print(".", end="", flush=True)
        
        print("\n⚠️  L'application ne répond pas, tentative d'arrêt forcé...")
        
        # Tenter un kill si nécessaire
        try:
            import signal
            # D'abord SIGTERM (arrêt propre)
            os.kill(pid, signal.SIGTERM)
            time.sleep(3)
            
            # Vérifier si le processus existe toujours
            try:
                os.kill(pid, 0)  # Test si le processus existe
                # Le processus existe encore, forcer avec SIGKILL
                print("⚠️  Force kill (SIGKILL)...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
            except OSError:
                # Le processus n'existe plus
                pass
            
            # Nettoyer les fichiers
            if os.path.exists(pid_file):
                os.remove(pid_file)
            if os.path.exists('pingu_headless.stop'):
                os.remove('pingu_headless.stop')
            
            print("✅ Application arrêtée de force")
            print("💡 Attendez 5 secondes avant de relancer pour que le port soit libéré")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Erreur lors de l'arrêt: {e}")
            print(f"💡 Vous pouvez essayer manuellement:")
            print(f"   kill -9 {pid}")
            print("   Ou utilisez: bash cleanup_raspberry.sh")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Utilisez le script de nettoyage: bash cleanup_raspberry.sh")


if __name__ == "__main__":
    import argparse
    
    # Parser les arguments de ligne de commande
    parser = argparse.ArgumentParser(
        description='Ping ü - Monitoring réseau',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python Pingu.py                    Lancer avec interface graphique (mode normal)
  python Pingu.py -start             Lancer en mode headless (sans interface, pour serveurs)
  python Pingu.py --start            Lancer en mode headless (alias)
  python Pingu.py -stop              Arrêter l'application en mode headless
  python Pingu.py --stop             Arrêter l'application en mode headless (alias)

Mode headless:
  Le mode headless est idéal pour les serveurs Linux sans interface graphique.
  L'application démarre le serveur web sur le port 9090.
  Accédez à l'interface admin via: http://localhost:9090/admin
  Identifiants par défaut: admin / a
        """
    )
    
    parser.add_argument('-start', '--start', action='store_true',
                       help='Démarrer en mode headless (sans interface graphique)')
    parser.add_argument('-headless', '--headless', action='store_true',
                       help='Alias pour --start (mode headless)')
    parser.add_argument('-stop', '--stop', action='store_true',
                       help='Arrêter l\'application en mode headless')
    
    args = parser.parse_args()
    
    if args.stop:
        # Mode stop
        stop_headless_mode()
    elif args.start or args.headless:
        # Mode headless
        run_headless_mode()
    else:
        # Mode normal avec interface graphique
        if not GUI_AVAILABLE:
            print("❌ Impossible de démarrer l'interface graphique: PySide6 n'est pas installé.")
            print("💡 Pour le mode serveur sans interface, utilisez: python Pingu.py --headless")
            sys.exit(1)
            
        from PySide6.QtWidgets import QSplashScreen
        from PySide6.QtGui import QPixmap
        app = QApplication(sys.argv)  # Créer l'application Qt
        pixmap = QPixmap(400, 200)
        pixmap.fill(QColor("white"))
        splash = QSplashScreen(pixmap)
        splash.showMessage("Chargement...", alignment=Qt.AlignCenter)
        splash.show()
        window = MainWindow()         # Instancier la fenêtre principale
        window.show()
        splash.finish(window)
        sys.exit(app.exec())
