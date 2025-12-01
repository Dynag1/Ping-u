# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QStatusBar, QTabWidget,
    QTreeView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.WindowModality.ApplicationModal)
        MainWindow.resize(800, 600)
        icon = QIcon()
        icon.addFile(u"src/img/logoP.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setTabShape(QTabWidget.TabShape.Triangular)
        MainWindow.setDockNestingEnabled(False)
        self.menuClose = QAction(MainWindow)
        self.menuClose.setObjectName(u"menuClose")
        self.actionSauvegarder = QAction(MainWindow)
        self.actionSauvegarder.setObjectName(u"actionSauvegarder")
        self.actionOuvrir = QAction(MainWindow)
        self.actionOuvrir.setObjectName(u"actionOuvrir")
        self.actionTout_effacer = QAction(MainWindow)
        self.actionTout_effacer.setObjectName(u"actionTout_effacer")
        self.actionSauvegarder_les_r_glages = QAction(MainWindow)
        self.actionSauvegarder_les_r_glages.setObjectName(u"actionSauvegarder_les_r_glages")
        self.actionG_n_raux = QAction(MainWindow)
        self.actionG_n_raux.setObjectName(u"actionG_n_raux")
        self.actionMail_recap = QAction(MainWindow)
        self.actionMail_recap.setObjectName(u"actionMail_recap")
        self.actionEnvoies = QAction(MainWindow)
        self.actionEnvoies.setObjectName(u"actionEnvoies")
        self.actionBase_de_donn_e = QAction(MainWindow)
        self.actionBase_de_donn_e.setObjectName(u"actionBase_de_donn_e")
        self.actionExporter_xls = QAction(MainWindow)
        self.actionExporter_xls.setObjectName(u"actionExporter_xls")
        self.actionImporter_xls = QAction(MainWindow)
        self.actionImporter_xls.setObjectName(u"actionImporter_xls")
        self.actionChangelog = QAction(MainWindow)
        self.actionChangelog.setObjectName(u"actionChangelog")
        self.actionLogs = QAction(MainWindow)
        self.actionLogs.setObjectName(u"actionLogs")
        self.actionEffacer_logs = QAction(MainWindow)
        self.actionEffacer_logs.setObjectName(u"actionEffacer_logs")
        self.actionG_rer = QAction(MainWindow)
        self.actionG_rer.setObjectName(u"actionG_rer")
        self.actiondf = QAction(MainWindow)
        self.actiondf.setObjectName(u"actiondf")
        self.actionAPropos = QAction(MainWindow)
        self.actionAPropos.setObjectName(u"actionAPropos")
        self.actionMaj = QAction(MainWindow)
        self.actionMaj.setObjectName(u"actionMaj")
        self.actionCleGpg = QAction(MainWindow)
        self.actionCleGpg.setObjectName(u"actionCleGpg")
        self.actionSnyf = QAction(MainWindow)
        self.actionSnyf.setObjectName(u"actionSnyf")
        self.actionSnyf_2 = QAction(MainWindow)
        self.actionSnyf_2.setObjectName(u"actionSnyf_2")
        self.actionNotice = QAction(MainWindow)
        self.actionNotice.setObjectName(u"actionNotice")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.formLayout = QFormLayout(self.centralwidget)
        self.formLayout.setObjectName(u"formLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame_haut = QFrame(self.centralwidget)
        self.frame_haut.setObjectName(u"frame_haut")
        self.frame_haut.setMinimumSize(QSize(0, 55))
        self.frame_haut.setMaximumSize(QSize(16777215, 55))
        self.frame_haut.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_haut.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_haut)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(1, 1, 1, 1)
        self.horizontalSpacer = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.label_7 = QLabel(self.frame_haut)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(50, 50))
        self.label_7.setMaximumSize(QSize(50, 50))
        self.label_7.setText(u"")
        self.label_7.setPixmap(QPixmap(u"img/logoP.png"))
        self.label_7.setScaledContents(True)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_7)

        self.horizontalSpacer_2 = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.butStart = QPushButton(self.frame_haut)
        self.butStart.setObjectName(u"butStart")
        self.butStart.setMinimumSize(QSize(50, 50))
        self.butStart.setMaximumSize(QSize(50, 50))
        self.butStart.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.butStart)

        self.horizontalSpacer_3 = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.labSite = QLabel(self.frame_haut)
        self.labSite.setObjectName(u"labSite")
        self.labSite.setMinimumSize(QSize(0, 0))
        self.labSite.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.labSite.setFont(font)
        self.labSite.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout_2.addWidget(self.labSite)

        self.horizontalSpacer_5 = QSpacerItem(10, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_5)

        self.progressBar = QProgressBar(self.frame_haut)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMinimumSize(QSize(100, 0))
        self.progressBar.setMaximumSize(QSize(200, 16777215))
        self.progressBar.setValue(24)

        self.horizontalLayout_2.addWidget(self.progressBar)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.gridLayout.addWidget(self.frame_haut, 0, 0, 1, 1)

        self.frame_bas = QFrame(self.centralwidget)
        self.frame_bas.setObjectName(u"frame_bas")
        self.frame_bas.setMinimumSize(QSize(0, 25))
        self.frame_bas.setMaximumSize(QSize(16777215, 25))
        self.frame_bas.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_bas.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_bas)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.labLic = QLabel(self.frame_bas)
        self.labLic.setObjectName(u"labLic")

        self.gridLayout_2.addWidget(self.labLic, 0, 2, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_6, 0, 3, 1, 1)

        self.labVersion1 = QLabel(self.frame_bas)
        self.labVersion1.setObjectName(u"labVersion1")
        self.labVersion1.setMinimumSize(QSize(0, 0))
        self.labVersion1.setMaximumSize(QSize(16777215, 16777215))
        self.labVersion1.setAutoFillBackground(False)

        self.gridLayout_2.addWidget(self.labVersion1, 0, 0, 1, 1)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_7, 0, 1, 1, 1)

        self.label_4 = QLabel(self.frame_bas)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 0, 4, 1, 1)


        self.gridLayout.addWidget(self.frame_bas, 2, 0, 1, 1)

        self.frame_mid = QFrame(self.centralwidget)
        self.frame_mid.setObjectName(u"frame_mid")
        self.frame_mid.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_mid.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_mid)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame = QFrame(self.frame_mid)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(200, 0))
        self.frame.setMaximumSize(QSize(200, 16777215))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.txtIp = QLineEdit(self.frame)
        self.txtIp.setObjectName(u"txtIp")
        self.txtIp.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.txtIp)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_2)

        self.spinHote = QSpinBox(self.frame)
        self.spinHote.setObjectName(u"spinHote")
        self.spinHote.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinHote.setMinimum(1)
        self.spinHote.setMaximum(255)
        self.spinHote.setValue(255)

        self.verticalLayout.addWidget(self.spinHote)

        self.txtAlive = QComboBox(self.frame)
        self.txtAlive.setObjectName(u"txtAlive")

        self.verticalLayout.addWidget(self.txtAlive)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label_3)

        self.txtPort = QLineEdit(self.frame)
        self.txtPort.setObjectName(u"txtPort")
        self.txtPort.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.txtPort)

        self.butIp = QPushButton(self.frame)
        self.butIp.setObjectName(u"butIp")

        self.verticalLayout.addWidget(self.butIp)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.frame)

        self.treeIp = QTreeView(self.frame_mid)
        self.treeIp.setObjectName(u"treeIp")
        self.treeIp.setAlternatingRowColors(False)
        self.treeIp.setUniformRowHeights(False)
        self.treeIp.setSortingEnabled(True)
        self.treeIp.header().setCascadingSectionResizes(True)
        self.treeIp.header().setMinimumSectionSize(0)
        self.treeIp.header().setHighlightSections(True)
        self.treeIp.header().setProperty(u"showSortIndicator", True)

        self.horizontalLayout.addWidget(self.treeIp)

        self.frame_2 = QFrame(self.frame_mid)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(200, 0))
        self.frame_2.setMaximumSize(QSize(200, 16777215))
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_4 = QFrame(self.frame_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_4)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_5 = QFrame(self.frame_4)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(self.frame_5)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 0))
        self.label_5.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_3.addWidget(self.label_5)

        self.spinDelais = QSpinBox(self.frame_5)
        self.spinDelais.setObjectName(u"spinDelais")
        self.spinDelais.setMinimum(5)
        self.spinDelais.setMaximum(20000)

        self.horizontalLayout_3.addWidget(self.spinDelais)

        self.labDelaisH = QLabel(self.frame_5)
        self.labDelaisH.setObjectName(u"labDelaisH")
        self.labDelaisH.setMaximumSize(QSize(50, 16777215))
        self.labDelaisH.setSizeIncrement(QSize(0, 0))

        self.horizontalLayout_3.addWidget(self.labDelaisH)


        self.verticalLayout_4.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.frame_4)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_6 = QLabel(self.frame_6)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout_4.addWidget(self.label_6)

        self.spinHs = QSpinBox(self.frame_6)
        self.spinHs.setObjectName(u"spinHs")
        self.spinHs.setMinimum(1)
        self.spinHs.setMaximum(100)
        self.spinHs.setValue(1)

        self.horizontalLayout_4.addWidget(self.spinHs)

        self.horizontalSpacer_8 = QSpacerItem(50, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)


        self.verticalLayout_4.addWidget(self.frame_6)


        self.verticalLayout_2.addWidget(self.frame_4)

        self.frame_7 = QFrame(self.frame_2)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_7)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.checkPopup = QCheckBox(self.frame_7)
        self.checkPopup.setObjectName(u"checkPopup")

        self.verticalLayout_5.addWidget(self.checkPopup)

        self.checkMail = QCheckBox(self.frame_7)
        self.checkMail.setObjectName(u"checkMail")

        self.verticalLayout_5.addWidget(self.checkMail)

        self.checkTelegram = QCheckBox(self.frame_7)
        self.checkTelegram.setObjectName(u"checkTelegram")

        self.verticalLayout_5.addWidget(self.checkTelegram)

        self.checkMailRecap = QCheckBox(self.frame_7)
        self.checkMailRecap.setObjectName(u"checkMailRecap")

        self.verticalLayout_5.addWidget(self.checkMailRecap)

        self.checkDbExterne = QCheckBox(self.frame_7)
        self.checkDbExterne.setObjectName(u"checkDbExterne")

        self.verticalLayout_5.addWidget(self.checkDbExterne)


        self.verticalLayout_2.addWidget(self.frame_7)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout.addWidget(self.frame_2)


        self.gridLayout.addWidget(self.frame_mid, 1, 0, 1, 1)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.gridLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuParametres = QMenu(self.menubar)
        self.menuParametres.setObjectName(u"menuParametres")
        self.menuLangue = QMenu(self.menuParametres)
        self.menuLangue.setObjectName(u"menuLangue")
        self.menuFonctions = QMenu(self.menubar)
        self.menuFonctions.setObjectName(u"menuFonctions")
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        #self.menuPlugin = QMenu(self.menubar)
        #self.menuPlugin.setObjectName(u"menuPlugin")
        #MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuParametres.menuAction())
        self.menubar.addAction(self.menuFonctions.menuAction())
        #self.menubar.addAction(self.menuPlugin.menuAction())
        self.menubar.addAction(self.menu.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSauvegarder)
        self.menuFile.addAction(self.actionOuvrir)
        self.menuFile.addAction(self.actionTout_effacer)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSauvegarder_les_r_glages)
        self.menuParametres.addAction(self.actionG_n_raux)
        self.menuParametres.addAction(self.actionEnvoies)
        self.menuParametres.addAction(self.actionMail_recap)
        self.menuParametres.addAction(self.actionCleGpg)
        self.menuParametres.addAction(self.actionBase_de_donn_e)
        self.menuParametres.addSeparator()
        self.menuParametres.addAction(self.menuLangue.menuAction())
        self.menuFonctions.addAction(self.actionExporter_xls)
        self.menuFonctions.addAction(self.actionImporter_xls)
        self.menuFonctions.addSeparator()
        self.menuFonctions.addAction(self.actionSnyf_2)
        self.menu.addAction(self.actionAPropos)
        self.menu.addAction(self.actionChangelog)
        self.menu.addAction(self.actionLogs)
        self.menu.addAction(self.actionEffacer_logs)
        self.menu.addSeparator()
        self.menu.addAction(self.actionMaj)
        self.menu.addAction(self.actionNotice)
        #self.menuPlugin.addAction(self.actionG_rer)
        #self.menuPlugin.addSeparator()

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Ping \u00fc", None))
        self.menuClose.setText(QCoreApplication.translate("MainWindow", u"Close", None))
        self.actionSauvegarder.setText(QCoreApplication.translate("MainWindow", u"Sauvegarder (ctrl+s)", None))
#if QT_CONFIG(shortcut)
        self.actionSauvegarder.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionOuvrir.setText(QCoreApplication.translate("MainWindow", u"Ouvrir (ctrl+o)", None))
#if QT_CONFIG(shortcut)
        self.actionOuvrir.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionTout_effacer.setText(QCoreApplication.translate("MainWindow", u"Tout effacer", None))
        self.actionSauvegarder_les_r_glages.setText(QCoreApplication.translate("MainWindow", u"Sauvegarder les r\u00e9glages", None))
        self.actionG_n_raux.setText(QCoreApplication.translate("MainWindow", u"G\u00e9n\u00e9raux", None))
        self.actionMail_recap.setText(QCoreApplication.translate("MainWindow", u"Mail recap", None))
        self.actionEnvoies.setText(QCoreApplication.translate("MainWindow", u"Envoies", None))
        self.actionBase_de_donn_e.setText(QCoreApplication.translate("MainWindow", u"Base de donn\u00e9e", None))
        self.actionExporter_xls.setText(QCoreApplication.translate("MainWindow", u"Exporter xls", None))
        self.actionImporter_xls.setText(QCoreApplication.translate("MainWindow", u"Importer xls", None))
        self.actionChangelog.setText(QCoreApplication.translate("MainWindow", u"Changelog", None))
        self.actionLogs.setText(QCoreApplication.translate("MainWindow", u"Logs", None))
        self.actionEffacer_logs.setText(QCoreApplication.translate("MainWindow", u"Effacer logs", None))
        self.actionG_rer.setText(QCoreApplication.translate("MainWindow", u"G\u00e9rer", None))
        self.actiondf.setText(QCoreApplication.translate("MainWindow", u"df", None))
        self.actionAPropos.setText(QCoreApplication.translate("MainWindow", u"A Propos", None))
        self.actionMaj.setText(QCoreApplication.translate("MainWindow", u"Recherche de mise \u00e0 jour", None))
        self.actionCleGpg.setText(QCoreApplication.translate("MainWindow", u"Cl\u00e9 GPG", None))
        self.actionSnyf.setText(QCoreApplication.translate("MainWindow", u"Snyf", None))
        self.actionSnyf_2.setText(QCoreApplication.translate("MainWindow", u"Snyf", None))
        self.actionNotice.setText(QCoreApplication.translate("MainWindow", u"Notice", None))
        self.butStart.setText(QCoreApplication.translate("MainWindow", u"Start", None))
#if QT_CONFIG(shortcut)
        self.butStart.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.labSite.setText("")
        self.labLic.setText("")
        self.labVersion1.setText(QCoreApplication.translate("MainWindow", u"a", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><a href=\"https://prog.dynag.co\"><span style=\" text-decoration: underline; color:#007af4;\">Copyright Dynag</span></a></p></body></html>", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"IP", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Nbr Hotes", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Ports XX,XX", None))
        self.butIp.setText(QCoreApplication.translate("MainWindow", u"Valider", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"D\u00e9lais", None))
        self.labDelaisH.setText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Nombre HS", None))
        self.checkPopup.setText(QCoreApplication.translate("MainWindow", u"PopUp", None))
        self.checkMail.setText(QCoreApplication.translate("MainWindow", u"Mail", None))
        self.checkTelegram.setText(QCoreApplication.translate("MainWindow", u"Telegram", None))
        self.checkMailRecap.setText(QCoreApplication.translate("MainWindow", u"Mail Recap", None))
        self.checkDbExterne.setText(QCoreApplication.translate("MainWindow", u"Db Externe", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"Fichier", None))
        self.menuParametres.setTitle(QCoreApplication.translate("MainWindow", u"Parametres", None))
        self.menuLangue.setTitle(QCoreApplication.translate("MainWindow", u"Langue", None))
        self.menuFonctions.setTitle(QCoreApplication.translate("MainWindow", u"Export / import", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"?", None))
        #self.menuPlugin.setTitle(QCoreApplication.translate("MainWindow", u"Plugin", None))
    # retranslateUi

