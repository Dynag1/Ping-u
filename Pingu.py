# This Python file uses the following encoding: utf-8
import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtWidgets import QAbstractItemView, QMessageBox, QMenu
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QAction, QActionGroup
from PySide6.QtCore import QObject, Signal, Qt, QPoint, QModelIndex, QTranslator, QEvent, QCoreApplication, QLocale, QSortFilterProxyModel
from src.ui_mainwindow import Ui_MainWindow
from src import var, fct, lic, threadAjIp, db, sFenetre
from src import fctXls, fctMaj
import src.Snyf.main as snyf
from src.controllers.settings_controller import SettingsController
from src.controllers.main_controller import MainController
from src.web_server import WebServer
import threading
import qt_themes
import webbrowser
import importlib
import platform


from src.utils.logger import setup_logging, get_logger

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
        try:
            # 1. Arrêter le flag global
            var.tourne = False
            
            # 2. Arrêter le monitoring via le contrôleur
            if hasattr(self, 'main_controller') and self.main_controller:
                self.main_controller.stop_monitoring()
            
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
                
            # 5. Attendre un peu pour que les threads se terminent
            # Note: QTimer.singleShot n'est pas idéal ici car on est dans closeEvent
            # On laisse le temps aux threads de voir var.tourne = False
            
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
        self.plugin = fct.plug(self)
        self.menuPlugin(self.plugin)
        
        self.ui.progressBar.hide()
        lic.verify_license()
        
        # Initialisation de l'arbre
        self.tree_view = self.ui.treeIp
        self.treeIpHeader(self.tree_view)
        # IP locale
        self.ui.txtIp.setText(fct.getIp(self))
        
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
        self.ui.actionG_rer.triggered.connect(self.plugGerer)
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
        self.treeIpModel = QStandardItemModel()
        # 10 colonnes uniquement (SANS Débit IN/OUT)
        self.treeIpModel.setHorizontalHeaderLabels([
            self.tr("Id"), self.tr("IP"), self.tr("Nom"), self.tr("Mac"), 
            self.tr("Port"), self.tr("Latence"), self.tr("Temp"), self.tr("Suivi"), 
            self.tr("Comm"), self.tr("Excl")
        ])
        
        # Utiliser un proxy model pour le tri numérique des IP
        self.proxyModel = IPSortProxyModel()
        self.proxyModel.setSourceModel(self.treeIpModel)
        self.tree_view.setModel(self.proxyModel)
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

        # Coloration selon is_ok
        couleur = QColor("#1f8137") if is_ok else QColor("#A9A9A9")
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
        var.nbrHs = value

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
        chemin = os.path.abspath("cle")
        if not os.path.exists(chemin):
            raise FileNotFoundError(f"Le dossier {chemin} n'existe pas.")
        systeme = platform.system()
        if systeme == "Windows":
            os.startfile(chemin)
        elif systeme == "Darwin":
            subprocess.run(["open", chemin])
        else:
            subprocess.run(["xdg-open", chemin])

    def notice(self):
        webbrowser.open("https://github.com/Atypi/Ping-u/blob/main/Notice.md")

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
            QMessageBox.critical(self, self.tr("Erreur"), f"{self.tr('Impossible d\'effacer les logs')}: {e}")
    
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
                self.web_server = WebServer(self, port=5000)
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
                                       self.tr("Impossible de démarrer le serveur web.\nLe port 5000 est peut-être déjà utilisé."))
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
                msg += self.tr("Note: Assurez-vous que le pare-feu autorise les connexions sur le port 5000.")
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


if __name__ == "__main__":
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
