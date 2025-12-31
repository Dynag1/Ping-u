# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fenParamEnvoie.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_fenParamEnvoie(object):
    def setupUi(self, fenParamEnvoie):
        if not fenParamEnvoie.objectName():
            fenParamEnvoie.setObjectName(u"fenParamEnvoie")
        fenParamEnvoie.resize(320, 282)
        self.verticalLayout = QVBoxLayout(fenParamEnvoie)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_6 = QFrame(fenParamEnvoie)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame_6)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.label)

        self.labCompte = QLineEdit(self.frame_6)
        self.labCompte.setObjectName(u"labCompte")

        self.horizontalLayout.addWidget(self.labCompte)


        self.verticalLayout.addWidget(self.frame_6)

        self.frame_3 = QFrame(fenParamEnvoie)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.frame_3)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_2.addWidget(self.label_2)

        self.labPass = QLineEdit(self.frame_3)
        self.labPass.setObjectName(u"labPass")

        self.horizontalLayout_2.addWidget(self.labPass)


        self.verticalLayout.addWidget(self.frame_3)

        self.frame_2 = QFrame(fenParamEnvoie)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.label_3)

        self.labPort = QLineEdit(self.frame_2)
        self.labPort.setObjectName(u"labPort")

        self.horizontalLayout_3.addWidget(self.labPort)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame = QFrame(fenParamEnvoie)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_4.addWidget(self.label_4)

        self.labServeur = QLineEdit(self.frame)
        self.labServeur.setObjectName(u"labServeur")

        self.horizontalLayout_4.addWidget(self.labServeur)


        self.verticalLayout.addWidget(self.frame)

        self.frame_5 = QFrame(fenParamEnvoie)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_5 = QLabel(self.frame_5)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(100, 0))
        self.label_5.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_5.addWidget(self.label_5)

        self.labMail = QLineEdit(self.frame_5)
        self.labMail.setObjectName(u"labMail")

        self.horizontalLayout_5.addWidget(self.labMail)


        self.verticalLayout.addWidget(self.frame_5)

        self.frame_4 = QFrame(fenParamEnvoie)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.frame_4)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(100, 0))
        self.label_6.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_6.addWidget(self.label_6)

        self.labTelegram = QLineEdit(self.frame_4)
        self.labTelegram.setObjectName(u"labTelegram")

        self.horizontalLayout_6.addWidget(self.labTelegram)


        self.verticalLayout.addWidget(self.frame_4)

        self.pushOk = QDialogButtonBox(fenParamEnvoie)
        self.pushOk.setObjectName(u"pushOk")
        self.pushOk.setOrientation(Qt.Orientation.Horizontal)
        self.pushOk.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.pushOk)


        self.retranslateUi(fenParamEnvoie)
        self.pushOk.accepted.connect(fenParamEnvoie.accept)
        self.pushOk.rejected.connect(fenParamEnvoie.reject)

        QMetaObject.connectSlotsByName(fenParamEnvoie)
    # setupUi

    def retranslateUi(self, fenParamEnvoie):
        fenParamEnvoie.setWindowTitle(QCoreApplication.translate("fenParamEnvoie", u"Param\u00e8tre des envoies", None))
        self.label.setText(QCoreApplication.translate("fenParamEnvoie", u"Compte", None))
        self.label_2.setText(QCoreApplication.translate("fenParamEnvoie", u"Mot de passe", None))
        self.label_3.setText(QCoreApplication.translate("fenParamEnvoie", u"Port", None))
        self.label_4.setText(QCoreApplication.translate("fenParamEnvoie", u"Serveur", None))
        self.label_5.setText(QCoreApplication.translate("fenParamEnvoie", u"Mail \u00e0 envoyer", None))
        self.label_6.setText(QCoreApplication.translate("fenParamEnvoie", u"Id T\u00e9l\u00e9gram", None))
    # retranslateUi

