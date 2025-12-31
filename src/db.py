from src import var
import pickle
import os.path
from pathlib import Path
try:
    from PySide6.QtCore import Qt
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    class Qt:
        DisplayRole = 0

from src.utils.logger import get_logger
from src.utils.paths import AppPaths

logger = get_logger(__name__)


"""**************
    Creer dossier
**************"""
fichierini = "tabG"


def creerDossier(nom):
    # Obsolète : Utiliser AppPaths.ensure_dirs() au démarrage
    # On garde pour compatibilité mais on utilise AppPaths
    try:
        AppPaths.ensure_dirs()
    except Exception as e:
        logger.error(f"Erreur création dossier {nom}: {e}")


def lireNom(ip, model):
    # Parcourir toutes les lignes
    for row in range(model.rowCount()):
        index_ip = model.index(row, 1)  # Colonne 0 = IP
        # Vérifier le match d'IP
        if model.data(index_ip, Qt.DisplayRole) == ip:
            # Récupérer colonne 3 (index 2)
            index_col3 = model.index(row, 2)
            print(ip)
            return model.data(index_col3, Qt.DisplayRole)
    return None  # Si non trouvé


"""***************
    Param Géné
***************"""


def nom_site():
    try:
        param = lire_param_gene()
        var.nom_site = param[0]
        var.l = param[1]
    except Exception as inst:
        logger.error(f"Erreur lecture nom site: {inst}", exc_info=True)
        return param[0]


def lire_param_gene():
    try:
        if os.path.isfile(fichierini):
            fichierSauvegarde = open(fichierini, "rb")
            variables = pickle.load(fichierSauvegarde)
            fichierSauvegarde.close()
            return variables
        else:
            logger.warning(f"Fichier {fichierini} non trouvé")
    except Exception as inst:
        logger.error(f"Erreur lecture param gene: {inst}", exc_info=True)


def save_param_gene(param_site, param_li, param_theme, param_advanced_title=None):
    try:
        if param_advanced_title is None:
            # Essayer de récupérer le titre existant pour ne pas l'écraser
            current = lire_param_gene()
            if current and len(current) > 3:
                param_advanced_title = current[3]
            else:
                param_advanced_title = "Paramètres Avancés"
        
        variables = [param_site, param_li, param_theme, param_advanced_title]
        fichierSauvegarde = open(fichierini, "wb")
        pickle.dump(variables, fichierSauvegarde)
        fichierSauvegarde.close()
    except Exception as inst:
        logger.error(f"Erreur sauvegarde param gene: {inst}", exc_info=True)


"""**************
    DB Param
**************"""


def lire_param_db():
    try:
        fichierini = "tab4"
        if os.path.isfile(fichierini):
            fichierSauvegarde = open(fichierini, "rb")
            variables = pickle.load(fichierSauvegarde)
            fichierSauvegarde.close()
            return variables
        else:
            logger.warning(f"Fichier {fichierini} non trouvé")
    except Exception as inst:
        logger.error(f"Erreur lecture param db: {inst}", exc_info=True)


def save_param_db():
    try:
        param_delais = var.delais
        param_nbr_hs = var.nbrHs
        param_popup = var.popup
        param_mail = var.mail
        param_telegram = var.telegram
        param_mail_recap = var.mailRecap
        param_db_ext = var.dbExterne
        param_temp_alert = var.tempAlert
        param_temp_seuil = var.tempSeuil
        param_temp_seuil_warning = var.tempSeuilWarning
        variables = [param_delais, param_nbr_hs, param_popup, param_mail, param_telegram, param_mail_recap, param_db_ext, param_temp_alert, param_temp_seuil, param_temp_seuil_warning]
        try:
            fichierSauvegarde = open("tab4", "wb")
            pickle.dump(variables, fichierSauvegarde)
            fichierSauvegarde.close()
        except Exception as inst:
            logger.error(f"Erreur sauvegarde param db (interne): {inst}", exc_info=True)
            return
    except Exception as inst:
        logger.error(f"Erreur sauvegarde param db: {inst}", exc_info=True)


def save_sites():
    """Sauvegarde les paramètres des sites (liste des sites et sites actifs)."""
    try:
        sites_data = {
            'sites_list': var.sites_list,
            'sites_actifs': var.sites_actifs,
            'site_filter': var.site_filter
        }
        with open("sites.pkl", "wb") as f:
            pickle.dump(sites_data, f)
        logger.info(f"Sites sauvegardés: {var.sites_list}")
    except Exception as e:
        logger.error(f"Erreur sauvegarde sites: {e}", exc_info=True)


def load_sites():
    """Charge les paramètres des sites."""
    try:
        if os.path.isfile("sites.pkl"):
            with open("sites.pkl", "rb") as f:
                sites_data = pickle.load(f)
            var.sites_list = sites_data.get('sites_list', ["Site 1"])
            var.sites_actifs = sites_data.get('sites_actifs', [])
            var.site_filter = sites_data.get('site_filter', [])
            logger.info(f"Sites chargés: {var.sites_list}")
        else:
            logger.info("Pas de fichier sites.pkl, utilisation des valeurs par défaut")
    except Exception as e:
        logger.error(f"Erreur chargement sites: {e}", exc_info=True)


def load_temp_alert_params(variables):
    """Charge les paramètres d'alerte température depuis les variables lues."""
    try:
        if len(variables) > 7:
            var.tempAlert = variables[7]
        if len(variables) > 8:
            var.tempSeuil = variables[8]
        if len(variables) > 9:
            var.tempSeuilWarning = variables[9]
    except Exception as e:
        logger.warning(f"Paramètres alerte température non trouvés, utilisation des valeurs par défaut: {e}")


"""**************
    DB Param Mail
**************"""


def lire_param_mail():
    fichierini = "tab"
    try:
        if os.path.isfile(fichierini):
            fichierSauvegarde = open(fichierini, "rb")
            variables = pickle.load(fichierSauvegarde)
            fichierSauvegarde.close()
            return variables
        else:
            logger.warning(f"Fichier {fichierini} non trouvé")
            return False
    except Exception as inst:
        logger.error(f"Erreur lecture param mail: {inst}", exc_info=True)


def save_param_mail(variables):
    try:
        fichierSauvegarde = open("tab", "wb")
        pickle.dump(variables, fichierSauvegarde)
        fichierSauvegarde.close()
    except Exception as inst:
        logger.error(f"Erreur sauvegarde param mail: {inst}", exc_info=True)
    return


"""***********************
    Parametres mail recap
**********************"""


def save_param_mail_recap(value):
    try:
        fichierSauvegarde = open("tabr","wb")
        pickle.dump(value, fichierSauvegarde)
        fichierSauvegarde.close()
    except Exception as inst:
        logger.error(f"Erreur sauvegarde param mail recap: {inst}", exc_info=True)
        return


def lire_param_mail_recap():
    fichierini = "tabr"
    try:
        if os.path.isfile(fichierini):
            fichierSauvegarde = open(fichierini, "rb")
            variables = pickle.load(fichierSauvegarde)
            fichierSauvegarde.close()

            # Affichage de la liste
            return variables
        else:
            # Le fichier n'existe pas
            logger.warning(f"Fichier {fichierini} non trouvé")
    except Exception as inst:
        logger.error(f"Erreur lecture param mail recap: {inst}", exc_info=True)
