# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fenParamGene.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(320, 240)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(100, 0))
        self.label.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout.addWidget(self.label)

        self.lineTitre = QLineEdit(self.frame)
        self.lineTitre.setObjectName(u"lineTitre")

        self.horizontalLayout.addWidget(self.lineTitre)


        self.verticalLayout.addWidget(self.frame)

        self.frame_5 = QFrame(Dialog)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.labTheme = QLabel(self.frame_5)
        self.labTheme.setObjectName(u"labTheme")
        self.labTheme.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout_5.addWidget(self.labTheme)

        self.comboTheme = QComboBox(self.frame_5)
        self.comboTheme.setObjectName(u"comboTheme")

        self.horizontalLayout_5.addWidget(self.comboTheme)


        self.verticalLayout.addWidget(self.frame_5)

        self.frame_4 = QFrame(Dialog)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(self.frame_4)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineCode = QLineEdit(self.frame_4)
        self.lineCode.setObjectName(u"lineCode")

        self.horizontalLayout_2.addWidget(self.lineCode)


        self.verticalLayout.addWidget(self.frame_4)

        self.frame_2 = QFrame(Dialog)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.frame_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.label_3)

        self.LineLicence = QLineEdit(self.frame_2)
        self.LineLicence.setObjectName(u"LineLicence")

        self.horizontalLayout_3.addWidget(self.LineLicence)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(Dialog)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.labLi = QLabel(self.frame_3)
        self.labLi.setObjectName(u"labLi")
        self.labLi.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_4.addWidget(self.labLi)


        self.verticalLayout.addWidget(self.frame_3)

        self.pushValid = QDialogButtonBox(Dialog)
        self.pushValid.setObjectName(u"pushValid")
        self.pushValid.setOrientation(Qt.Orientation.Horizontal)
        self.pushValid.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.pushValid)


        self.retranslateUi(Dialog)
        self.pushValid.accepted.connect(Dialog.accept)
        self.pushValid.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Titre ", None))
        self.labTheme.setText(QCoreApplication.translate("Dialog", u"Th\u00e8me", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Code ", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Licence", None))
        self.labLi.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
    # retranslateUi

