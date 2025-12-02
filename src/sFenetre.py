import sqlite3
from src import var, db, lic

try:
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtCore import Qt, QSortFilterProxyModel, Signal, QObject
    from PySide6.QtWidgets import QHeaderView, QDialog, QTimeEdit, QMessageBox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    # Classes factices minimales
    class QStandardItemModel: pass
    class QStandardItem: pass
    class Qt: pass
    class QSortFilterProxyModel: pass
    class Signal: 
        def __init__(self, *args): pass
        def emit(self, *args): pass
    class QObject: pass
    class QHeaderView: pass
    class QDialog: pass
    class QTimeEdit: pass
    class QMessageBox: 
        Accepted = 1


"""*******************************
    Paramètres
*******************************"""


def fenetreParametre(self, comm):
    if not GUI_AVAILABLE:
        return
    from src.ui_fenParamGene import Ui_Dialog
    try:
        resutl = db.lire_param_gene()
    except:
        print("")
    dialog = QDialog()
    sfenetre = Ui_Dialog()
    sfenetre.setupUi(dialog)


    try:
        titre = resutl[0]
        code = lic.generate_activation_code()
        licence = resutl[1]
        theme_actuel = resutl[2]
        def list_themes():
            themes = ["nord", "monokai", "catppuccin_latte", "catppuccin_frappe","catppuccin_mocha",
                "atom_one", "github_dark", "github_light", "dracula", "blender"]
            return themes
        themes = list_themes()
        for theme_name in themes:
            sfenetre.comboTheme.addItem(theme_name)

        sfenetre.comboTheme.setCurrentText(theme_actuel)

        sfenetre.lineTitre.setText(titre)
        sfenetre.lineCode.setText(code)
        sfenetre.LineLicence.setText(licence)


    except:
        print("")

    liActive = lic.verify_license()
    print(liActive)
    if liActive:
        sfenetre.labLi.setText(self.tr("Votre licence est active, il vous reste ")
                               + lic.jours_restants_licence()+self.tr(" jours"))
    else:
        sfenetre.labLi.setText(self.tr("Vous n'avez pas de license valide"))

    resultat = dialog.exec()
    #   result = self.ui.exec()
    if resultat == QMessageBox.Accepted:
        titre = sfenetre.lineTitre.text()
        code = sfenetre.lineCode.text()
        license = sfenetre.LineLicence.text()
        theme = sfenetre.comboTheme.currentText()
        db.save_param_gene(titre, license, theme)
        self.comm = comm
        comm.relaodWindow.emit(True)


def fenetreParamEnvoie(self):
    if not GUI_AVAILABLE:
        return
    from src.ui_fenParamEnvoie import Ui_fenParamEnvoie
    # resutl = db.lire_param_gene()
    dialog = QDialog()
    sfenetre = Ui_fenParamEnvoie()
    sfenetre.setupUi(dialog)

    def save_param_mail():
        param_mail_compte = sfenetre.labCompte.text()
        param_mail_pass = sfenetre.labPass.text()
        param_mail_port = sfenetre.labPort.text()
        param_mail_serveur = sfenetre.labServeur.text()
        param_mail_envoie = sfenetre.labMail.text()
        param_mail_telegram = sfenetre.labTelegram.text()
        variables = [param_mail_compte, param_mail_pass, param_mail_port, param_mail_serveur, param_mail_envoie, param_mail_telegram]
        db.save_param_mail(variables)

    def lire():
        try:
            variables = db.lire_param_mail()
            sfenetre.labCompte.setText(variables[0])
            sfenetre.labPass.setText(variables[1])
            sfenetre.labPort.setText(variables[2])
            sfenetre.labServeur.setText(variables[3])
            sfenetre.labMail.setText(variables[4])
            sfenetre.labTelegram.setText(variables[5])
        except Exception as inst:
            print(inst)
    try:
        lire()
    except:
        print("pas de ficheier")

    resultat = dialog.exec()
    if resultat == QMessageBox.Accepted:
        save_param_mail()


def fenetreMailRecap(self):
    if not GUI_AVAILABLE:
        return
    from src.ui_fenMailRecap import Ui_fenMailRecap
    # resutl = db.lire_param_gene()
    dialog = QDialog()
    sfenetre = Ui_fenMailRecap()
    sfenetre.setupUi(dialog)

    def save_param_mail():
        param_mail_heure = sfenetre.labHeure.time()
        param_mail_heure = param_mail_heure.toPython()
        param_mail_lundi = sfenetre.checkLundi.isChecked()
        param_mail_mardi = sfenetre.checkMardi.isChecked()
        param_mail_mercredi = sfenetre.checkMercredi.isChecked()
        param_mail_jeudi = sfenetre.checkJeudi.isChecked()
        param_mail_vendredi = sfenetre.checkVendredi.isChecked()
        param_mail_samedi = sfenetre.checkSamedi.isChecked()
        param_mail_dimanche = sfenetre.checkDimanche.isChecked()

        variables = [param_mail_heure, param_mail_lundi, param_mail_mardi, param_mail_mercredi,
                    param_mail_jeudi, param_mail_vendredi, param_mail_samedi, param_mail_dimanche]
        print(variables)
        db.save_param_mail_recap(variables)

    def lire():
        try:
            variables = db.lire_param_mail_recap()
            sfenetre.labHeure.setTime(variables[0])
            sfenetre.checkLundi.setChecked(variables[1])
            sfenetre.checkMardi.setChecked(variables[2])
            sfenetre.checkMercredi.setChecked(variables[3])
            sfenetre.checkJeudi.setChecked(variables[4])
            sfenetre.checkVendredi.setChecked(variables[5])
            sfenetre.checkSamedi.setChecked(variables[6])
            sfenetre.checkDimanche.setChecked(variables[7])
        except Exception as inst:
            print(inst)
    try:
        lire()
    except:
        print("pas de ficheier")

    resultat = dialog.exec()
    if resultat == QMessageBox.Accepted:
        save_param_mail()
def fenAPropos(self):
    if not GUI_AVAILABLE:
        return
    from src.ui_fenAPropos import Ui_Dialog
    dialog = QDialog()
    sfenetre = Ui_Dialog()
    sfenetre.setupUi(dialog)
    dialog.exec()
