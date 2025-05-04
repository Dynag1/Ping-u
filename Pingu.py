# This Python file uses the following encoding: utf-8
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QHeaderView
from PySide6.QtWidgets import QAbstractItemView, QMessageBox, QMenu, QDialog
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor, QAction, QActionGroup
from PySide6.QtCore import QObject, Signal, Qt, QPoint, QModelIndex, QTranslator, QEvent, QCoreApplication, QLocale
from src.ui_mainwindow import Ui_MainWindow
from src import var, fct, lic, threadAjIp, threadLancement, db, sFenetre
from src import fctXls, fctMaj
from src.fcy_ping import PingManager
import threading
import qdarktheme
import webbrowser
import importlib


class Communicate(QObject):
    addRow = Signal(str, str, str, str, str, str, bool)
    progress = Signal(int)
    relaodWindow = Signal(bool)


class MainWindow(QMainWindow):


    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def closeEvent(self, event):
        os._exit(0)
        event.accept()

    def __init__(self):

        super().__init__()
        self.translators = []
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.translator = QTranslator()
        try:
            theme = db.lire_param_gene()
            qdarktheme.setup_theme(theme[2])
        except:
            qdarktheme.setup_theme("dark")
        self.create_language_menu()
        self.comm = Communicate()
        self.tree_view = self.ui.treeIp
        self.load_language(QLocale().name()[:2])
        self.demarre()

    def demarre(self):
        # fctMaj.main()
        try:
            fctMaj.main(self)
        except Exception:
            return
        if lic.verify_license() == False:
            self.ui.checkMail.setEnabled(False)
            self.ui.checkDbExterne.setEnabled(False)
            self.ui.checkTelegram.setEnabled(False)
            self.ui.checkMailRecap.setEnabled(False)
        self.connector()
        self.plugin = fct.plug(self)
        self.menuPlugin(self.plugin)
        self.ui.progressBar.hide()
        lic.verify_license()
        self.tree_view = self.ui.treeIp
        self.treeIpHeader(self.tree_view)
        self.ui.txtIp.setText(fct.getIp(self))

        self.lireParamUi()

    def connector(self):
        self.ui.butIp.clicked.connect(self.butIpClic)
        self.ui.butStart.clicked.connect(self.butStart)
        self.ui.menuClose.triggered.connect(self.close)
        self.ui.actionG_rer.triggered.connect(self.plugGerer)
        # Modele alertes
        self.ui.spinDelais.valueChanged.connect(self.on_spin_delais_changed)
        self.ui.spinHs.valueChanged.connect(self.on_spin_spinHs_changed)
        self.ui.checkPopup.clicked.connect(self.popup)
        self.ui.checkMail.clicked.connect(self.mail)
        self.ui.checkTelegram.clicked.connect(self.telegram)
        self.ui.checkMailRecap.clicked.connect(self.mailRecap)
        self.ui.checkDbExterne.clicked.connect(self.pingDb)
        # Fentres
        self.ui.actionSauvegarder_les_r_glages.triggered.connect(lambda: self.saveParam)
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
        # Communication
        self.comm.relaodWindow.connect(self.reload_main_window)
        self.comm.addRow.connect(self.on_add_row)
        self.comm.progress.connect(self.barProgress)


    """********************
        Traduction
    ********************"""
    def get_language_path(self):
        if getattr(sys, 'frozen', False):
            # Mode compilé : chemin dans le bundle
            base_path = sys._MEIPASS
        else:
            # Mode développement : chemin relatif
            base_path = os.path.dirname(__file__)

        return os.path.join(base_path, 'src', 'languages')

    # Utilisation dans votre code


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


    def retranslateUi(self):
        # Réinitialise toute l'interface
        _translate = QCoreApplication.translate
        self.ui.retranslateUi(self)  # Si vous utilisez un UI chargé
        self.langReload()

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

    def change_language(self, action):
        lang_code = action.data()
        self.load_language(lang_code)
        self.retranslateUi()

    def langReload(self):
        print("lang")
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

    """ *******************************
        Plugin
    ********************************"""

    def menuPlugin(self, plugin):
        try:
            for plug in plugin:
                #self.ui.menuPlugin.addMenu(plug)
                action_directe = QAction(plug, self)
                action_directe.triggered.connect(lambda checked=False, p=plug: self.pluginLance(p))
                # Ajout direct de l'action dans le menu (PAS dans un sous-menu)
                self.ui.menuPlugin.addAction(action_directe)
        except Exception as e:
            QMessageBox.information(
                self,
                "Erreur",
                str(e),
                QMessageBox.Ok
            )

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
            print(e)
            print("design - " + str(e))

    def lireParamUi(self):
        try:
            variable = db.lire_param_db()
            var.delais = variable[0]
            var.envoie_alert = variable[1]
            var.popup = variable[2]
            var.mail = variable[3]
            var.telegram = variable[4]
            var.mailRecap = variable[5]
            db.nom_site()
            self.ui.labSite.setText(var.nom_site)
            self.ui.spinDelais.setValue(int(var.delais))
            self.ui.spinHs.setValue(int(var.envoie_alert))
            if var.popup is True:
                self.ui.checkPopup.setChecked(True)
            if var.mail is True:
                self.ui.checkMail.setChecked(True)
            if var.telegram is True:
                self.ui.checkTelegram.setChecked(True)
            if var.mailRecap is True:
                self.ui.checkMailRecap.setChecked(True)
        except Exception as inst:
            print(inst)
        db.creerDossier("bd")
        db.creerDossier("fichier")
        db.creerDossier("fichier/plugin")

    def saveParam(self):
        db.save_param_db()

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
        var.tourne = False
        app.aboutToQuit.connect(self.cleanup_threads)
        os._exit(0)

    def treeIpHeader(self, tree_view):
        self.tree_view = self.ui.treeIp
        self.treeIpModel = QStandardItemModel()
        self.treeIpModel.setHorizontalHeaderLabels([self.tr("Id"), self.tr("IP"), self.tr("Nom"), self.tr("Mac"), self.tr("Port"), self.tr("Latence"), self.tr("Suivi"), self.tr("Comm"), self.tr("Excl")])
        self.tree_view.setModel(self.treeIpModel)
        header = self.tree_view.header()
        header.setStretchLastSection(False)
        for i in range(self.treeIpModel.columnCount()):
            if i in [0, 5, 6, 8]:  # Colonnes figées
                header.setSectionResizeMode(i, QHeaderView.Fixed)
            else:  # Colonnes étirables
                header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.tree_view.setColumnWidth(0, 1)
        self.tree_view.setColumnWidth(5, 50)
        self.tree_view.setColumnWidth(6, 50)
        self.tree_view.setColumnWidth(8, 50)
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
        print(f"Ouverture de {ip_item.text()}")

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
            QStandardItem(i),
            QStandardItem(ip),
            QStandardItem(nom),
            QStandardItem(mac),
            QStandardItem(str(port)),
            QStandardItem(extra),
            QStandardItem(""),
            QStandardItem(""),
            QStandardItem("")
        ]
        if is_ok:
            for item in items:
                item.setBackground(QColor("#1f8137"))
        else:
            for item in items:
                item.setBackground(QColor("#A9A9A9"))
        self.treeIpModel.appendRow(items)

    def butStart(self):
        self.ping_manager = PingManager(self.treeIpModel)
        if self.ui.butStart.isChecked():
            var.tourne = True
            self.ping_manager.start()
            threading.Thread(target=threadLancement.main, args=(self, self.treeIpModel)).start()
        else:
            var.tourne = False
            self.ping_manager.stop()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Créer l'application Qt
    window = MainWindow()         # Instancier la fenêtre principale
    window.show()                 # Afficher la fenêtre principale
    sys.exit(app.exec())         # Exécuter la boucle d'événements
