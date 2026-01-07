# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fen.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFrame,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 400)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labTitre = QLabel(Dialog)
        self.labTitre.setObjectName(u"labTitre")
        self.labTitre.setMinimumSize(QSize(0, 50))
        self.labTitre.setMaximumSize(QSize(16777215, 50))
        font = QFont()
        font.setPointSize(11)
        self.labTitre.setFont(font)
        self.labTitre.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.labTitre)

        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.frame_3)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 50))
        self.label.setMaximumSize(QSize(16777215, 50))
        font1 = QFont()
        font1.setPointSize(11)
        font1.setBold(True)
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)

        self.checkOnvif = QCheckBox(self.frame_3)
        self.checkOnvif.setObjectName(u"checkOnvif")

        self.verticalLayout_2.addWidget(self.checkOnvif)

        self.checkHik = QCheckBox(self.frame_3)
        self.checkHik.setObjectName(u"checkHik")

        self.verticalLayout_2.addWidget(self.checkHik)

        self.checkSamsung = QCheckBox(self.frame_3)
        self.checkSamsung.setObjectName(u"checkSamsung")

        self.verticalLayout_2.addWidget(self.checkSamsung)

        self.checkXiaomi = QCheckBox(self.frame_3)
        self.checkXiaomi.setObjectName(u"checkXiaomi")

        self.verticalLayout_2.addWidget(self.checkXiaomi)

        self.checkAvigilon = QCheckBox(self.frame_3)
        self.checkAvigilon.setObjectName(u"checkAvigilon")

        self.verticalLayout_2.addWidget(self.checkAvigilon)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)


        self.horizontalLayout_2.addWidget(self.frame_3)

        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_2 = QLabel(self.frame_4)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 50))
        self.label_2.setMaximumSize(QSize(16777215, 50))
        self.label_2.setFont(font1)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_2)

        self.checkUpnp = QCheckBox(self.frame_4)
        self.checkUpnp.setObjectName(u"checkUpnp")

        self.verticalLayout_3.addWidget(self.checkUpnp)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addWidget(self.frame_4)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(Dialog)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMaximumSize(QSize(16777215, 50))
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushValid = QPushButton(self.frame_2)
        self.pushValid.setObjectName(u"pushValid")

        self.horizontalLayout.addWidget(self.pushValid)

        self.pushAnnule = QPushButton(self.frame_2)
        self.pushAnnule.setObjectName(u"pushAnnule")

        self.horizontalLayout.addWidget(self.pushAnnule)

        self.pushCocher = QPushButton(self.frame_2)
        self.pushCocher.setObjectName(u"pushCocher")
        self.horizontalLayout.addWidget(self.pushCocher)

        self.pushDecocher = QPushButton(self.frame_2)
        self.pushDecocher.setObjectName(u"pushDecocher")
        self.horizontalLayout.addWidget(self.pushDecocher)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frame_2)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Snyf", None))
        self.labTitre.setText("")
        self.label.setText(QCoreApplication.translate("Dialog", u"Cam\u00e9ras", None))
        self.checkOnvif.setText(QCoreApplication.translate("Dialog", u"Onvif", None))
        self.checkHik.setText(QCoreApplication.translate("Dialog", u"Hik Vision", None))
        self.checkSamsung.setText(QCoreApplication.translate("Dialog", u"Samsung", None))
        self.checkXiaomi.setText(QCoreApplication.translate("Dialog", u"Xiaomi", None))
        self.checkAvigilon.setText(QCoreApplication.translate("Dialog", u"Avigilon", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Autres", None))
        self.checkUpnp.setText(QCoreApplication.translate("Dialog", u"Upnp", None))
        self.pushValid.setText(QCoreApplication.translate("Dialog", u"Valider", None))
        self.pushAnnule.setText(QCoreApplication.translate("Dialog", u"Annuler", None))
        self.pushCocher.setText(QCoreApplication.translate("Dialog", u"Tout cocher", None))
        self.pushDecocher.setText(QCoreApplication.translate("Dialog", u"Tout décocher", None))
    # retranslateUi

