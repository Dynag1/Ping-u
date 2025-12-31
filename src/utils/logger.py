import logging
import os
from logging.handlers import RotatingFileHandler
import sys

def setup_logging(log_dir="logs", log_file="app.log", level=logging.INFO):
    """
    Configure le système de logging pour l'application.
    Utilise AppData si l'application est dans Program Files (pas de droits d'écriture).
    """
    # Déterminer le chemin des logs
    try:
        os.makedirs(log_dir, exist_ok=True)
        # Tester si on peut écrire
        test_file = os.path.join(log_dir, ".write_test")
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
    except (PermissionError, OSError):
        # Utiliser AppData/Local si pas de permissions
        app_data = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'Ping_u')
        log_dir = os.path.join(app_data, 'logs')
        os.makedirs(log_dir, exist_ok=True)
    
    log_path = os.path.join(log_dir, log_file)
    
    # Configuration du format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour fichier avec rotation
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(level)
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(level)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Nettoyer les handlers existants pour éviter les doublons
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.info(f"Logging initialisé. Fichier: {log_path}")

def get_logger(name):
    """
    Récupère un logger nommé pour un module spécifique.
    
    Args:
        name (str): Nom du module (généralement __name__)
        
    Returns:
        logging.Logger: Instance du logger configuré
    """
    return logging.getLogger(name)
