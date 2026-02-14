from src import var
from src import secure_config
from src.utils.logger import get_logger
from src.utils.paths import AppPaths
import os.path
from datetime import datetime, time

# Conditional Import for Qt Constants if needed, largely for 'lireNom'
try:
    from PySide6.QtCore import Qt
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    class Qt:
        DisplayRole = 0

logger = get_logger(__name__)

"""**************
    Creer dossier
**************"""
fichierini = "bd/tabs/tabG" # Legacy path kept for compatibility ref, but unused logic

def creerDossier(nom):
    # Obsolète : Utiliser AppPaths.ensure_dirs() au démarrage
    try:
        # secure_config.ensure_config_dir() is called by save functions
        pass 
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
        return "Ping ü"

def lire_param_gene():
    try:
        config = secure_config.load_general_config()
        # Return format: [param_site, param_li, param_theme, param_advanced_title]
        return [
            config.get('site_name', "Ping ü"),
            config.get('license_key', ""),
            config.get('theme', "nord"),
            config.get('advanced_title', "Paramètres Avancés")
        ]
    except Exception as inst:
        logger.error(f"Erreur lecture param gene: {inst}", exc_info=True)
        return ["Ping ü", "", "nord", "Paramètres Avancés"]

def save_param_gene(param_site, param_li, param_theme, param_advanced_title=None):
    try:
        if param_advanced_title is None:
            # Essayer de récupérer le titre existant pour ne pas l'écraser
            current = secure_config.load_general_config()
            param_advanced_title = current.get('advanced_title', "Paramètres Avancés")
        
        secure_config.save_general_config(
            site_name=param_site,
            license_key=param_li,
            theme=param_theme,
            advanced_title=param_advanced_title
        )
    except Exception as inst:
        logger.error(f"Erreur sauvegarde param gene: {inst}", exc_info=True)


"""**************
    DB Param
**************"""

def lire_param_db():
    try:
        config = secure_config.load_alerts_config()
        # Return format: [delais, nbr_hs, popup, mail, telegram, mail_recap, db_ext, temp_alert, temp_seuil, temp_seuil_warning]
        return [
            config.get('delai', 10),
            config.get('nb_hs', 3),
            config.get('popup', False),
            config.get('mail', False),
            config.get('telegram', False),
            config.get('mail_recap', False),
            config.get('db_externe', False),
            config.get('temp_alert', False),
            config.get('temp_seuil', 70),
            config.get('temp_seuil_warning', 60)
        ]
    except Exception as inst:
        logger.error(f"Erreur lecture param db: {inst}", exc_info=True)
        return [10, 3, False, False, False, False, False, False, 70, 60]

def save_param_db():
    try:
        secure_config.save_alerts_config(
            delai=var.delais,
            nb_hs=var.nbrHs,
            popup=var.popup,
            mail=var.mail,
            telegram=var.telegram,
            mail_recap=var.mailRecap,
            db_externe=var.dbExterne,
            temp_alert=var.tempAlert,
            temp_seuil=var.tempSeuil,
            temp_seuil_warning=var.tempSeuilWarning
        )
    except Exception as inst:
        logger.error(f"Erreur sauvegarde param db: {inst}", exc_info=True)


def save_sites():
    """Sauvegarde les paramètres des sites (liste des sites et sites actifs)."""
    try:
        secure_config.save_sites_config(
            sites_list=var.sites_list,
            sites_actifs=var.sites_actifs,
            site_filter=var.site_filter
        )
        logger.info(f"Sites sauvegardés: {var.sites_list}")
    except Exception as e:
        logger.error(f"Erreur sauvegarde sites: {e}", exc_info=True)


def load_sites():
    """Charge les paramètres des sites."""
    try:
        config = secure_config.load_sites_config()
        var.sites_list = config.get('sites_list', ["Site 1"])
        var.sites_actifs = config.get('sites_actifs', [])
        var.site_filter = config.get('site_filter', [])
        logger.info(f"Sites chargés: {var.sites_list}")
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
    try:
        config = secure_config.load_mail_config()
        # Legacy format expected: [email, password, port, server, recipients_string, telegram_chat_id]
        recipients = config.get('recipients', [])
        recipients_str = ",".join(recipients) if isinstance(recipients, list) else str(recipients)
        
        # Get Telegram Chat IDs
        tg_chat_ids = secure_config.get_telegram_chat_ids()
        tg_chat_str = ",".join(tg_chat_ids) if isinstance(tg_chat_ids, list) else str(tg_chat_ids)
        
        return [
            config.get('email', ""),
            config.get('password', ""),
            str(config.get('smtp_port', 587)),
            config.get('smtp_server', ""),
            recipients_str,
            tg_chat_str
        ]
    except Exception as inst:
        logger.error(f"Erreur lecture param mail: {inst}", exc_info=True)
        return ["", "", "587", "", "", ""]

def save_param_mail(variables):
    try:
        # variables: [email, password, port, server, recipient_str, telegram_chat_id]
        
        email = variables[0]
        password = variables[1]
        port = variables[2]
        server = variables[3]
        recipients = [r.strip() for r in variables[4].split(',') if r.strip()]
        
        secure_config.save_mail_config(
            email=email,
            password=password,
            smtp_port=port,
            smtp_server=server,
            recipients=recipients
        )
        
        # Save Telegram Chat ID if present (index 5)
        if len(variables) > 5:
            tg_chat_str = variables[5]
            tg_chat_ids = [c.strip() for c in tg_chat_str.split(',') if c.strip()]
            secure_config.save_telegram_config(chat_ids=tg_chat_ids)
            
    except Exception as inst:
        logger.error(f"Erreur sauvegarde param mail: {inst}", exc_info=True)


"""***********************
    Parametres mail recap
**********************"""

def save_param_mail_recap(value):
    try:
        # value expected: [time_obj, Mon, Tue, ... Sun]
        # time_obj can be datetime.time or QTime
        time_obj = value[0] if len(value) > 0 else None
        time_str = "08:00"
        
        if hasattr(time_obj, 'strftime'):
            time_str = time_obj.strftime("%H:%M")
        elif hasattr(time_obj, 'toString'):
            time_str = time_obj.toString("HH:mm")
        elif isinstance(time_obj, str):
            time_str = time_obj
            
        days = value[1:] if len(value) > 1 else []
        
        recap_config = {
            'schedule_time': time_str,
            'days': days
        }
        secure_config._save_json("bd/config/mail_recap.json", recap_config)
        
    except Exception as inst:
        logger.error(f"Erreur sauvegarde param mail recap: {inst}", exc_info=True)


def lire_param_mail_recap():
    try:
        recap_config = secure_config._load_json("bd/config/mail_recap.json", {'schedule_time': "08:00", 'days': [True]*7})
        
        time_str = recap_config.get('schedule_time', "08:00")
        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            time_obj = time(8, 0)
            
        days = recap_config.get('days', [True]*7)
        
        # Return: [time_obj, day1, day2...]
        return [time_obj] + days
        
    except Exception as inst:
        logger.error(f"Erreur lecture param mail recap: {inst}", exc_info=True)
        return [time(8, 0)] + [True]*7
