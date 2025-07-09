# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fenAPropos.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(480, 400)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.label)

        self.textAPropos = QTextEdit(Dialog)
        self.textAPropos.setObjectName(u"textAPropos")
        font1 = QFont()
        font1.setPointSize(11)
        self.textAPropos.setFont(font1)
        self.textAPropos.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByKeyboard|Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextBrowserInteraction|Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout.addWidget(self.textAPropos)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"A Propos", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"A Propos", None))
        self.textAPropos.setMarkdown(QCoreApplication.translate("Dialog", u"**_Ping \u00fc**_\n"
"\n"
"Ping \u00fc est un logiciel de Ping r\u00e9seau.\n"
"\n"
"Il permet de retrouver les h\u00f4tes actifs et de les suivre. Une alerte est\n"
"envoy\u00e9e si un des h\u00f4te tombe.\n"
"\n"
"Site internet : <https://prog.dynag.co>\n"
"\n"
"Plugins disponibles : <https://prog.dynag.co/pyngouin/>\n"
"\n"
"**_Fonctionnalit\u00e9s**_\n"
"\n"
"\\- Recherche des h\u00f4tes actifs\n"
"\n"
"\\- Ping des h\u00f4tes, d\u00e9lais entre 2 pings r\u00e9glable\n"
"\n"
"\\- Popup, envoie de mail, envoie sur t\u00e9l\u00e9grame en cas de perte ou de     retour\n"
"d'un h\u00f4te\n"
"\n"
"\\- R\u00e9capitulatif hebdomadaire possible\n"
"\n"
"\\- Export et import des IP sous excel\n"
"\n"
"**_Cr\u00e9dits**_\n"
"\n"
"\\- Concepteur : Hemg\u00e9\n"
"\n"
"\\- Correctrice : Gally\n"
"\n"
"[Code source](https://github.com/Dynag1/Ping-u)\n"
"\n"
"", None))
        self.textAPropos.setHtml(QCoreApplication.translate("Dialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-weight:700; text-decoration: underline;\">Ping \u00fc</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -"
                        "qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Ping \u00fc est un logiciel de Ping r\u00e9seau.</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Il permet de retrouver les h\u00f4tes actifs et de les suivre. Une alerte est envoy\u00e9e si un des h\u00f4te tombe.</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Site internet : </span><a href=\"https://prog.dynag.co\"><span style=\" text-decoration: underline; color:#007af4;\">https://prog.dynag.co</span></a></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:"
                        "0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Plugins disponibles : </span><a href=\"https://prog.dynag.co/pyngouin/\"><span style=\" text-decoration: underline; color:#007af4;\">https://prog.dynag.co/pyngouin/</span></a></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; text-decoration: underline; color:#007af4;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700; text-decoration: underline;\">Fonctionnalit\u00e9s</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">- Recherche des h\u00f4tes actifs</span></p>\n"
"<p align=\"justify\" style=\" mar"
                        "gin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">- Ping des h\u00f4tes, d\u00e9lais entre 2 pings r\u00e9glable</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">- Popup, envoie de mail, envoie sur t\u00e9l\u00e9grame en cas de perte ou de     retour d'un h\u00f4te</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">- R\u00e9capitulatif hebdomadaire possible</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">- Export et import des IP sous excel</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-t"
                        "op:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700; text-decoration: underline;\">Cr\u00e9dits</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">- Concepteur : Hemg\u00e9</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">- Correctrice : Gally</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; mar"
                        "gin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/Dynag1/Ping-u\"><span style=\" text-decoration: underline; color:#007af4;\">Code source</span></a></p></body></html>", None))
    # retranslateUi

