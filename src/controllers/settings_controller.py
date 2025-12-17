from src import db, var
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SettingsController:
    def __init__(self, main_window):
        self.ui = main_window.ui
        self.main_window = main_window

    def load_ui_settings(self):
        """Charge les paramètres depuis la DB et met à jour l'UI."""
        try:
            variable = db.lire_param_db()
            if variable and len(variable) >= 6:
                var.delais = variable[0]
                var.nbrHs = variable[1]
                var.envoie_alert = variable[1]  # Compatibilité ancien code
                var.popup = variable[2]
                var.mail = variable[3]
                var.telegram = variable[4]
                var.mailRecap = variable[5]
                
                if len(variable) > 6:
                    var.dbExterne = variable[6]
                if len(variable) > 7:
                    var.tempAlert = variable[7]
                if len(variable) > 8:
                    var.tempSeuil = variable[8]
            
            # Charger les sites
            db.load_sites()
            
            db.nom_site()
            self.ui.labSite.setText(var.nom_site)
            self.ui.spinDelais.setValue(int(var.delais))
            self.ui.spinHs.setValue(int(var.nbrHs))
            
            if var.popup is True:
                self.ui.checkPopup.setChecked(True)
            if var.mail is True:
                self.ui.checkMail.setChecked(True)
            if var.telegram is True:
                self.ui.checkTelegram.setChecked(True)
            if var.mailRecap is True:
                self.ui.checkMailRecap.setChecked(True)
            if var.dbExterne is True:
                self.ui.checkDbExterne.setChecked(True)
            
            # Paramètres alerte température
            if hasattr(self.ui, 'checkTempAlert') and hasattr(var, 'tempAlert'):
                self.ui.checkTempAlert.setChecked(var.tempAlert)
            if hasattr(self.ui, 'spinTempSeuil') and hasattr(var, 'tempSeuil'):
                self.ui.spinTempSeuil.setValue(int(var.tempSeuil))
                
        except Exception as e:
            logger.error(f"Erreur chargement paramètres UI: {e}", exc_info=True)
            
        # Création des dossiers nécessaires (logique existante)
        db.creerDossier("bd")
        db.creerDossier("fichier")
        db.creerDossier("fichier/plugin")

    def save_settings(self):
        """Sauvegarde les paramètres dans la DB."""
        try:
            db.save_param_db()
            logger.info("Paramètres sauvegardés via SettingsController")
        except Exception as e:
            logger.error(f"Erreur sauvegarde paramètres: {e}", exc_info=True)
