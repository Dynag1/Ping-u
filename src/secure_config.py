# -*- coding: utf-8 -*-
"""
Module de configuration sécurisé pour Ping ü
Utilise JSON au lieu de Pickle pour éviter les vulnérabilités de désérialisation
SÉCURITÉ: Ce module remplace progressivement db.py
"""
import os
import json
from pathlib import Path
from datetime import time, datetime
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    class Fernet:
        """Implémentation Dummy si cryptography n'est pas installé"""
        def __init__(self, key): pass
        @staticmethod
        def generate_key(): return b'dummy_key'
        def encrypt(self, data): return data
        def decrypt(self, data): return data

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Chemins des fichiers de configuration JSON
CONFIG_DIR = "bd/config"
TELEGRAM_CONFIG_FILE = os.path.join(CONFIG_DIR, "telegram.json")
MAIL_CONFIG_FILE = os.path.join(CONFIG_DIR, "mail.json")
GENERAL_CONFIG_FILE = os.path.join(CONFIG_DIR, "general.json")
ALERTS_CONFIG_FILE = os.path.join(CONFIG_DIR, "alerts.json")
SITES_CONFIG_FILE = os.path.join(CONFIG_DIR, "sites.json")
SECRET_KEY_FILE = "bd/secret.key"

_fernet_instance = None


def _get_fernet():
    """Récupère ou crée l'instance Fernet pour le chiffrement"""
    global _fernet_instance
    if _fernet_instance:
        return _fernet_instance
    
    try:
        if not CRYPTOGRAPHY_AVAILABLE:
            return Fernet(b'')

        # Créer le dossier si nécessaire (devrait déjà être fait)
        os.makedirs(os.path.dirname(SECRET_KEY_FILE), exist_ok=True)
        
        if os.path.exists(SECRET_KEY_FILE):
            with open(SECRET_KEY_FILE, 'rb') as f:
                key = f.read()
        else:
            logger.info("Génération d'une nouvelle clé de chiffrement")
            key = Fernet.generate_key()
            with open(SECRET_KEY_FILE, 'wb') as f:
                f.write(key)
        
        _fernet_instance = Fernet(key)
        return _fernet_instance
    except Exception as e:
        logger.error(f"Erreur initialisation chiffrement: {e}")
        # Fallback temporaire pour ne pas crasher
        return Fernet(Fernet.generate_key())

def _encrypt_string(data):
    """Chiffre une chaîne de caractères"""
    if not data:
        return ""
    try:
        if not CRYPTOGRAPHY_AVAILABLE:
            return data
        return _get_fernet().encrypt(data.encode()).decode()
    except Exception as e:
        logger.error(f"Erreur chiffrement: {e}")
        return ""

def _decrypt_string(token):
    """Déchiffre une chaîne de caractères"""
    if not token:
        return ""
    try:
        if not CRYPTOGRAPHY_AVAILABLE:
            return token
        return _get_fernet().decrypt(token.encode()).decode()
    except Exception as e:
        # Si échec, c'est peut-être que ce n'est pas chiffré (legacy)
        return token


def ensure_config_dir():
    """Crée le répertoire de configuration s'il n'existe pas"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
    except Exception as e:
        logger.error(f"Erreur création répertoire config: {e}")


def _load_json(filepath, default=None):
    """Charge un fichier JSON de manière sécurisée"""
    try:
        if os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except json.JSONDecodeError as e:
        logger.error(f"Erreur JSON invalide dans {filepath}: {e}")
        return default
    except Exception as e:
        logger.error(f"Erreur lecture {filepath}: {e}")
        return default


def _save_json(filepath, data):
    """Sauvegarde un fichier JSON de manière sécurisée"""
    try:
        ensure_config_dir()
        # Écriture atomique via fichier temporaire
        temp_path = filepath + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        os.replace(temp_path, filepath)
        return True
    except Exception as e:
        logger.error(f"Erreur sauvegarde {filepath}: {e}")
        return False


# ============================================
# Configuration Telegram
# ============================================

def load_telegram_config():
    """Charge la configuration Telegram"""
    default = {
        'token': '',  # Token du bot (JAMAIS exposé via API)
        'chat_ids': [],  # Liste des chat IDs
        'enabled': False
    }
    return _load_json(TELEGRAM_CONFIG_FILE, default)


def save_telegram_config(token=None, chat_ids=None, enabled=None):
    """Sauvegarde la configuration Telegram"""
    config = load_telegram_config()
    if token is not None:
        config['token'] = token
    if chat_ids is not None:
        config['chat_ids'] = chat_ids if isinstance(chat_ids, list) else [chat_ids]
    if enabled is not None:
        config['enabled'] = enabled
    return _save_json(TELEGRAM_CONFIG_FILE, config)


def get_telegram_token():
    """Récupère le token Telegram (usage interne uniquement, JAMAIS via API)"""
    config = load_telegram_config()
    return config.get('token', '')


def get_telegram_chat_ids():
    """Récupère les chat IDs Telegram"""
    config = load_telegram_config()
    return config.get('chat_ids', [])


# ============================================
# Configuration Mail
# ============================================

def load_mail_config():
    """Charge la configuration mail"""
    default = {
        'smtp_server': '',
        'smtp_port': 587,
        'email': '',
        'password': '',  # TODO: chiffrer avec cryptography
        'recipients': [],
        'use_tls': True
    }
    config = _load_json(MAIL_CONFIG_FILE, default)
    
    # Déchiffrer le mot de passe
    if config.get('password'):
        # Tenter de déchiffrer. Si ça échoue (token invalid), _decrypt_string renvoie la chaine telle quelle
        # Ce qui permet une migration automatique au prochain save
        config['password'] = _decrypt_string(config['password'])
        
    return config


def save_mail_config(smtp_server=None, smtp_port=None, email=None, 
                     password=None, recipients=None, use_tls=None):
    """Sauvegarde la configuration mail"""
    config = load_mail_config()
    
    # Mise à jour des valeurs
    if smtp_server is not None:
        config['smtp_server'] = smtp_server
    if smtp_port is not None:
        config['smtp_port'] = int(smtp_port)
    if email is not None:
        config['email'] = email
    
    # Si nouveau mot de passe fourni, on le met à jour en CLAIR dans l'objet config (mémoire)
    if password is not None:
        config['password'] = password
    
    # Sauvegarde
    data_to_save = config.copy()
    
    # On chiffre le mot de passe UNIQUEMENT pour la sauvegarde sur disque
    if data_to_save.get('password'):
        data_to_save['password'] = _encrypt_string(data_to_save['password'])

    if recipients is not None:
        data_to_save['recipients'] = recipients if isinstance(recipients, list) else recipients.split(',')
    
    if use_tls is not None:
        data_to_save['use_tls'] = use_tls
        
    return _save_json(MAIL_CONFIG_FILE, data_to_save)


# ============================================
# Configuration Générale
# ============================================

def load_general_config():
    """Charge la configuration générale"""
    default = {
        'site_name': 'Ping ü',
        'license_key': '',
        'theme': 'nord',
        'advanced_title': 'Paramètres Avancés',
        'language': 'fr'
    }
    return _load_json(GENERAL_CONFIG_FILE, default)


def save_general_config(**kwargs):
    """Sauvegarde la configuration générale"""
    config = load_general_config()
    for key, value in kwargs.items():
        if value is not None:
            config[key] = value
    return _save_json(GENERAL_CONFIG_FILE, config)


# ============================================
# Configuration Alertes
# ============================================

def load_alerts_config():
    """Charge la configuration des alertes"""
    default = {
        'delai': 10,
        'nb_hs': 3,
        'popup': False,
        'mail': False,
        'telegram': False,
        'mail_recap': False,
        'db_externe': False,
        'temp_alert': False,
        'temp_seuil': 70,
        'temp_seuil_warning': 60
    }
    return _load_json(ALERTS_CONFIG_FILE, default)


def save_alerts_config(**kwargs):
    """Sauvegarde la configuration des alertes"""
    config = load_alerts_config()
    for key, value in kwargs.items():
        if value is not None:
            config[key] = value
    return _save_json(ALERTS_CONFIG_FILE, config)


# ============================================
# Configuration Sites
# ============================================

def load_sites_config():
    """Charge la configuration des sites"""
    default = {
        'sites_list': ['Site 1'],
        'sites_actifs': [],
        'site_filter': []
    }
    return _load_json(SITES_CONFIG_FILE, default)


def save_sites_config(**kwargs):
    """Sauvegarde la configuration des sites"""
    config = load_sites_config()
    for key, value in kwargs.items():
        if value is not None:
            config[key] = value
    return _save_json(SITES_CONFIG_FILE, config)


# ============================================
# Validation des entrées
# ============================================

def validate_ip(ip):
    """Valide une adresse IP v4"""
    import re
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    octets = ip.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)


def validate_port(port):
    """Valide un numéro de port"""
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (ValueError, TypeError):
        return False


def sanitize_string(s, max_length=255, allowed_chars=None):
    """Nettoie une chaîne de caractères"""
    if not isinstance(s, str):
        return ''
    s = s.strip()[:max_length]
    if allowed_chars:
        s = ''.join(c for c in s if c in allowed_chars)
    return s
