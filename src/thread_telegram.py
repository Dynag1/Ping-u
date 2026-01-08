# This Python file uses the following encoding: utf-8
"""
Module d'envoi de messages Telegram
SÉCURITÉ: Le token est stocké dans la configuration, JAMAIS hardcodé
"""
import json
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Import optionnel de requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None


def get_telegram_credentials():
    """
    Récupère les credentials Telegram de manière sécurisée.
    Essaie d'abord le nouveau système (secure_config), puis fallback sur l'ancien (db).
    """
    # Essayer le nouveau système de configuration sécurisé
    try:
        from src import secure_config
        token = secure_config.get_telegram_token()
        chat_ids = secure_config.get_telegram_chat_ids()
        if token and chat_ids:
            return token, chat_ids
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"Erreur lecture config sécurisée Telegram: {e}")
    
    # Fallback sur l'ancien système (db.lire_param_mail)
    try:
        from src import db
        variables = db.lire_param_mail()
        if variables and len(variables) > 5:
            chat_ids_str = variables[5]
            if chat_ids_str:
                # L'ancien système stocke les chat_ids dans variables[5]
                # Le token doit maintenant être dans secure_config
                # On ne retourne que les chat_ids, le token doit être configuré
                try:
                    from src import secure_config
                    token = secure_config.get_telegram_token()
                    if token:
                        return token, chat_ids_str.split(",")
                except:
                    pass
                logger.warning("Token Telegram non configuré dans secure_config")
    except Exception as e:
        logger.error(f"Erreur lecture config Telegram: {e}")
    
    return None, []


def main(message):
    """Envoie un message à tous les chat IDs configurés"""
    if not REQUESTS_AVAILABLE:
        logger.warning("Telegram non disponible: module 'requests' manquant")
        return
    
    token, chat_ids = get_telegram_credentials()
    
    if not token:
        logger.error("Token Telegram non configuré. Utilisez l'interface d'administration.")
        return
    
    if not chat_ids:
        logger.warning("Aucun chat ID Telegram configuré")
        return
    
    for chat_id in chat_ids:
        chat_id = chat_id.strip()
        if chat_id:
            send_telegram_message(message, chat_id, token)


def send_telegram_message(message, chat_id, token=None):
    """
    Envoie un message Telegram à un chat spécifique.
    
    Args:
        message: Le message à envoyer
        chat_id: L'ID du chat destinataire
        token: Le token du bot (si non fourni, récupéré de la config)
    
    Returns:
        Response ou message d'erreur
    """
    if not REQUESTS_AVAILABLE:
        return "Module requests non disponible"
    
    if not token:
        token, _ = get_telegram_credentials()
        if not token:
            logger.error("Token Telegram non configuré")
            return "Token non configuré"
    
    headers = {
        'Content-Type': 'application/json'
    }
    data_dict = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_notification': False
    }
    data = json.dumps(data_dict)
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    
    try:
        response = requests.post(
            url,
            data=data,
            headers=headers,
            timeout=10,
            verify=True  # SÉCURITÉ: Vérifier les certificats SSL
        )
        if response.status_code == 200:
            logger.info(f"Message Telegram envoyé au chat {chat_id}")
        else:
            logger.warning(f"Erreur Telegram {response.status_code}: {response.text}")
        return response
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'envoi du message Telegram")
        return "Timeout"
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur réseau Telegram: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"Erreur envoi Telegram: {e}")
        return str(e)
