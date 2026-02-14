import pickle
import os
import shutil
from src import secure_config
from src.utils.logger import get_logger

logger = get_logger(__name__)

def get_pickle_path(filename):
    if os.path.exists(filename):
        return filename
    elif os.path.exists(filename + ".bak"):
        return filename + ".bak"
    return None

def migrate_general_config():
    """Migrate bd/tabs/tabG -> bd/config/general.json"""
    pickle_file = get_pickle_path("bd/tabs/tabG")
    if pickle_file:
        try:
            with open(pickle_file, "rb") as f:
                data = pickle.load(f)
            
            # Legacy structure: [param_site, param_li, param_theme, param_advanced_title]
            config = {
                'site_name': data[0] if len(data) > 0 else "Ping ü",
                'license_key': data[1] if len(data) > 1 else "",
                'theme': data[2] if len(data) > 2 else "nord",
                'advanced_title': data[3] if len(data) > 3 else "Paramètres Avancés"
            }
            
            secure_config.save_general_config(**config)
            logger.info("Migrated General Config")
            if not pickle_file.endswith(".bak"):
                shutil.move(pickle_file, pickle_file + ".bak")
        except Exception as e:
            logger.error(f"Failed to migrate General Config: {e}")

def migrate_alert_config():
    """Migrate bd/tabs/tab4 -> bd/config/alerts.json"""
    pickle_file = get_pickle_path("bd/tabs/tab4")
    if pickle_file:
        try:
            with open(pickle_file, "rb") as f:
                data = pickle.load(f)
            
            # Legacy: [delais, nbr_hs, popup, mail, telegram, mail_recap, db_ext, temp_alert, temp_seuil, temp_seuil_warning]
            config = {
                'delai': data[0] if len(data) > 0 else 10,
                'nb_hs': data[1] if len(data) > 1 else 3,
                'popup': data[2] if len(data) > 2 else False,
                'mail': data[3] if len(data) > 3 else False,
                'telegram': data[4] if len(data) > 4 else False,
                'mail_recap': data[5] if len(data) > 5 else False,
                'db_externe': data[6] if len(data) > 6 else False,
                'temp_alert': data[7] if len(data) > 7 else False,
                'temp_seuil': data[8] if len(data) > 8 else 70,
                'temp_seuil_warning': data[9] if len(data) > 9 else 60
            }
            
            secure_config.save_alerts_config(**config)
            logger.info("Migrated Alert Config")
            if not pickle_file.endswith(".bak"):
                shutil.move(pickle_file, pickle_file + ".bak")
        except Exception as e:
            logger.error(f"Failed to migrate Alert Config: {e}")

def migrate_mail_config():
    """Migrate bd/tabs/tab -> bd/config/mail.json"""
    pickle_file = get_pickle_path("bd/tabs/tab")
    if pickle_file:
        try:
            with open(pickle_file, "rb") as f:
                data = pickle.load(f)
            
            # Legacy: [email, password, port, server, recipient]
            # Based on thread_mail.py analysis
            recipients_raw = data[4] if len(data) > 4 else ""
            if isinstance(recipients_raw, str):
                recipients = [r.strip() for r in recipients_raw.split(',') if r.strip()]
            else:
                recipients = recipients_raw
                
            config = {
                'email': data[0] if len(data) > 0 else "",
                'password': data[1] if len(data) > 1 else "",
                'smtp_port': int(data[2]) if len(data) > 2 else 587,
                'smtp_server': data[3] if len(data) > 3 else "",
                'recipients': recipients,
                'use_tls': True
            }
            
            secure_config.save_mail_config(**config)
            logger.info("Migrated Mail Config")
            if not pickle_file.endswith(".bak"):
                shutil.move(pickle_file, pickle_file + ".bak")
        except Exception as e:
            logger.error(f"Failed to migrate Mail Config: {e}")

def migrate_mail_recap_config():
    """Migrate bd/tabs/tabr -> bd/config/mail_recap.json"""
    # Structure: [time_obj, Mon, Tue, Wed, Thu, Fri, Sat, Sun]
    
    pickle_file = get_pickle_path("bd/tabs/tabr")
    if pickle_file:
        try:
            with open(pickle_file, "rb") as f:
                data = pickle.load(f)
            
            time_obj = data[0] if len(data) > 0 else None
            
            time_str = "08:00"
            if hasattr(time_obj, 'strftime'):
                time_str = time_obj.strftime("%H:%M")
            elif hasattr(time_obj, 'toString'): # QTime
                time_str = time_obj.toString("HH:mm")
            elif isinstance(time_obj, str):
                time_str = time_obj
            
            days = []
            if len(data) > 1:
                days = data[1:]
                
            recap_config = {
                'schedule_time': time_str,
                'days': days
            }
            
            # We'll save this manually for now as secure_config needs update or specific function
            secure_config._save_json("bd/config/mail_recap.json", recap_config)
            
            logger.info("Migrated Mail Recap Config")
            if not pickle_file.endswith(".bak"):
                shutil.move(pickle_file, pickle_file + ".bak")
        except Exception as e:
            logger.error(f"Failed to migrate Mail Recap Config: {e}")

def migrate_sites_config():
    """Migrate sites.pkl -> bd/config/sites.json"""
    pickle_file = get_pickle_path("sites.pkl")
    if pickle_file:
        try:
            with open(pickle_file, "rb") as f:
                data = pickle.load(f)
            
            config = {
                'sites_list': data.get('sites_list', ["Site 1"]),
                'sites_actifs': data.get('sites_actifs', []),
                'site_filter': data.get('site_filter', [])
            }
            
            secure_config.save_sites_config(**config)
            logger.info("Migrated Sites Config")
            if not pickle_file.endswith(".bak"):
                shutil.move(pickle_file, pickle_file + ".bak")
        except Exception as e:
            logger.error(f"Failed to migrate Sites Config: {e}")

def run_migration():
    secure_config.ensure_config_dir()
    migrate_general_config()
    migrate_alert_config()
    migrate_mail_config()
    migrate_mail_recap_config()
    migrate_sites_config()
    print("Migration completed.")

if __name__ == "__main__":
    run_migration()
