# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fenMailRecap.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFrame, QHBoxLayout, QLabel,
    QSizePolicy, QTimeEdit, QVBoxLayout, QWidget)

class Ui_fenMailRecap(object):
    def setupUi(self, fenMailRecap):
        if not fenMailRecap.objectName():
            fenMailRecap.setObjectName(u"fenMailRecap")
        fenMailRecap.resize(320, 240)
        self.verticalLayout = QVBoxLayout(fenMailRecap)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(fenMailRecap)
        self.frame.setObjectName(u"frame")
        self.frame.setMaximumSize(QSize(16777215, 50))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.labHeure = QTimeEdit(self.frame)
        self.labHeure.setObjectName(u"labHeure")

        self.horizontalLayout.addWidget(self.labHeure)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(fenMailRecap)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame_3 = QFrame(self.frame_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkLundi = QCheckBox(self.frame_3)
        self.checkLundi.setObjectName(u"checkLundi")

        self.verticalLayout_2.addWidget(self.checkLundi)

        self.checkMercredi = QCheckBox(self.frame_3)
        self.checkMercredi.setObjectName(u"checkMercredi")

        self.verticalLayout_2.addWidget(self.checkMercredi)

        self.checkVendredi = QCheckBox(self.frame_3)
        self.checkVendredi.setObjectName(u"checkVendredi")

        self.verticalLayout_2.addWidget(self.checkVendredi)

        self.checkDimanche = QCheckBox(self.frame_3)
        self.checkDimanche.setObjectName(u"checkDimanche")

        self.verticalLayout_2.addWidget(self.checkDimanche)


        self.horizontalLayout_2.addWidget(self.frame_3)

        self.frame_4 = QFrame(self.frame_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_4)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.checkMardi = QCheckBox(self.frame_4)
        self.checkMardi.setObjectName(u"checkMardi")

        self.verticalLayout_3.addWidget(self.checkMardi)

        self.checkJeudi = QCheckBox(self.frame_4)
        self.checkJeudi.setObjectName(u"checkJeudi")

        self.verticalLayout_3.addWidget(self.checkJeudi)

        self.checkSamedi = QCheckBox(self.frame_4)
        self.checkSamedi.setObjectName(u"checkSamedi")

        self.verticalLayout_3.addWidget(self.checkSamedi)

        self.label_2 = QLabel(self.frame_4)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 15))
        self.label_2.setMaximumSize(QSize(16777215, 15))

        self.verticalLayout_3.addWidget(self.label_2)


        self.horizontalLayout_2.addWidget(self.frame_4)


        self.verticalLayout.addWidget(self.frame_2)

        self.buttonBox = QDialogButtonBox(fenMailRecap)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(fenMailRecap)
        self.buttonBox.accepted.connect(fenMailRecap.accept)
        self.buttonBox.rejected.connect(fenMailRecap.reject)

        QMetaObject.connectSlotsByName(fenMailRecap)
    # setupUi

    def retranslateUi(self, fenMailRecap):
        fenMailRecap.setWindowTitle(QCoreApplication.translate("fenMailRecap", u"Parametres mail recap", None))
        self.label.setText(QCoreApplication.translate("fenMailRecap", u"Heure de d\u00e9clenchement", None))
        self.checkLundi.setText(QCoreApplication.translate("fenMailRecap", u"Lundi", None))
        self.checkMercredi.setText(QCoreApplication.translate("fenMailRecap", u"Mercredi", None))
        self.checkVendredi.setText(QCoreApplication.translate("fenMailRecap", u"Vendredi", None))
        self.checkDimanche.setText(QCoreApplication.translate("fenMailRecap", u"Dimanche", None))
        self.checkMardi.setText(QCoreApplication.translate("fenMailRecap", u"Mardi", None))
        self.checkJeudi.setText(QCoreApplication.translate("fenMailRecap", u"Jeudi", None))
        self.checkSamedi.setText(QCoreApplication.translate("fenMailRecap", u"Samedi", None))
        self.label_2.setText("")
    # retranslateUi

