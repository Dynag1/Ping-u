# -*- coding: utf-8 -*-
"""
Module d'authentification pour le serveur web
"""
import os
import json
import hashlib
from functools import wraps
from flask import session, redirect, url_for, request
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WebAuth:
    def __init__(self, config_file='web_users.json'):
        """Initialise le système d'authentification"""
        self.config_file = config_file
        self.ensure_config_exists()
    
    def ensure_config_exists(self):
        """Crée le fichier de configuration avec l'utilisateur par défaut si nécessaire"""
        if not os.path.exists(self.config_file):
            # Créer l'utilisateur par défaut : admin / a
            default_user = {
                'username': 'admin',
                'password': self.hash_password('a')
            }
            self.save_credentials(default_user['username'], default_user['password'])
            logger.info("Fichier de configuration créé avec l'utilisateur par défaut")
    
    def hash_password(self, password):
        """Hash un mot de passe avec SHA256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def load_credentials(self):
        """Charge les identifiants depuis le fichier"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur chargement credentials: {e}")
            # Retourner l'utilisateur par défaut en cas d'erreur
            return {
                'username': 'admin',
                'password': self.hash_password('a')
            }
    
    def save_credentials(self, username, password_hash):
        """Sauvegarde les identifiants dans le fichier"""
        try:
            credentials = {
                'username': username,
                'password': password_hash
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=4)
            logger.info(f"Credentials sauvegardés pour l'utilisateur: {username}")
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde credentials: {e}")
            return False
    
    def verify_credentials(self, username, password):
        """Vérifie les identifiants"""
        credentials = self.load_credentials()
        password_hash = self.hash_password(password)
        
        if credentials['username'] == username and credentials['password'] == password_hash:
            logger.info(f"Connexion réussie pour l'utilisateur: {username}")
            return True
        else:
            logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {username}")
            return False
    
    def change_credentials(self, old_password, new_username, new_password):
        """Change les identifiants (nécessite l'ancien mot de passe)"""
        credentials = self.load_credentials()
        old_password_hash = self.hash_password(old_password)
        
        # Vérifier l'ancien mot de passe
        if credentials['password'] != old_password_hash:
            logger.warning("Tentative de changement de credentials avec mauvais mot de passe")
            return False, "Mot de passe actuel incorrect"
        
        # Sauvegarder les nouveaux identifiants
        new_password_hash = self.hash_password(new_password)
        if self.save_credentials(new_username, new_password_hash):
            return True, "Identifiants modifiés avec succès"
        else:
            return False, "Erreur lors de la sauvegarde"
    
    @staticmethod
    def login_required(f):
        """Décorateur pour protéger les routes"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session or not session['logged_in']:
                # Si c'est une requête API, retourner 401
                if request.path.startswith('/api/'):
                    from flask import jsonify
                    return jsonify({'success': False, 'error': 'Non authentifié'}), 401
                # Sinon rediriger vers la page de login
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

# Instance globale
web_auth = WebAuth()

