# -*- coding: utf-8 -*-
"""
Module d'authentification pour le serveur web
Support multi-utilisateurs avec rôles (admin, user)
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
        """Crée le fichier de configuration avec les utilisateurs par défaut si nécessaire"""
        if not os.path.exists(self.config_file):
            # Créer les utilisateurs par défaut
            default_users = {
                'users': [
                    {
                        'username': 'admin',
                        'password': self.hash_password('a'),
                        'role': 'admin'
                    },
                    {
                        'username': 'user',
                        'password': self.hash_password('a'),
                        'role': 'user'
                    }
                ]
            }
            self.save_all_users(default_users)
            logger.info("Fichier de configuration créé avec les utilisateurs par défaut (admin/a et user/a)")
        else:
            # Migration: si ancien format (un seul utilisateur), convertir
            self._migrate_old_format()
    
    def _migrate_old_format(self):
        """Migre l'ancien format (un utilisateur) vers le nouveau (multi-utilisateurs)"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Si c'est l'ancien format (pas de clé 'users')
            if 'users' not in data and 'username' in data:
                logger.info("Migration de l'ancien format de credentials...")
                old_user = {
                    'username': data['username'],
                    'password': data['password'],
                    'role': 'admin'
                }
                new_data = {
                    'users': [
                        old_user,
                        {
                            'username': 'user',
                            'password': self.hash_password('a'),
                            'role': 'user'
                        }
                    ]
                }
                self.save_all_users(new_data)
                logger.info("Migration terminée")
        except Exception as e:
            logger.error(f"Erreur lors de la migration: {e}")
    
    def hash_password(self, password):
        """Hash un mot de passe avec SHA256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def load_all_users(self):
        """Charge tous les utilisateurs depuis le fichier"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('users', [])
        except Exception as e:
            logger.error(f"Erreur chargement users: {e}")
            # Retourner les utilisateurs par défaut en cas d'erreur
            return [
                {'username': 'admin', 'password': self.hash_password('a'), 'role': 'admin'},
                {'username': 'user', 'password': self.hash_password('a'), 'role': 'user'}
            ]
    
    def save_all_users(self, data):
        """Sauvegarde tous les utilisateurs"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde users: {e}")
            return False
    
    def load_credentials(self):
        """Charge les identifiants admin (compatibilité)"""
        users = self.load_all_users()
        for user in users:
            if user.get('role') == 'admin':
                return user
        return {'username': 'admin', 'password': self.hash_password('a'), 'role': 'admin'}
    
    def save_credentials(self, username, password_hash):
        """Sauvegarde les identifiants admin (compatibilité)"""
        users = self.load_all_users()
        for user in users:
            if user.get('role') == 'admin':
                user['username'] = username
                user['password'] = password_hash
                break
        return self.save_all_users({'users': users})
    
    def verify_credentials(self, username, password):
        """Vérifie les identifiants et retourne le rôle si succès"""
        users = self.load_all_users()
        password_hash = self.hash_password(password)
        
        for user in users:
            if user['username'] == username and user['password'] == password_hash:
                logger.info(f"Connexion réussie pour l'utilisateur: {username} (role: {user.get('role', 'user')})")
                return True, user.get('role', 'user')
        
        logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {username}")
        return False, None
    
    def change_credentials(self, old_password, new_username, new_password):
        """Change les identifiants admin (nécessite l'ancien mot de passe)"""
        users = self.load_all_users()
        old_password_hash = self.hash_password(old_password)
        
        # Trouver l'admin
        for user in users:
            if user.get('role') == 'admin':
                if user['password'] != old_password_hash:
                    logger.warning("Tentative de changement de credentials avec mauvais mot de passe")
                    return False, "Mot de passe actuel incorrect"
                
                # Modifier les identifiants admin
                user['username'] = new_username
                user['password'] = self.hash_password(new_password)
                
                if self.save_all_users({'users': users}):
                    return True, "Identifiants modifiés avec succès"
                else:
                    return False, "Erreur lors de la sauvegarde"
        
        return False, "Utilisateur admin non trouvé"
    
    def change_user_credentials(self, target_role, new_username, new_password, current_password=None, current_username=None):
        """
        Change les identifiants d'un utilisateur par son rôle.
        - Si current_password est fourni, on vérifie l'ancien mot de passe (pour l'utilisateur lui-même)
        - Si appelé par un admin pour un autre utilisateur, current_password n'est pas requis
        """
        users = self.load_all_users()
        
        for user in users:
            if user.get('role') == target_role:
                # Si current_password est fourni, vérifier
                if current_password:
                    if user['password'] != self.hash_password(current_password):
                        return False, "Mot de passe actuel incorrect"
                
                # Vérifier que le nouveau username n'existe pas déjà (sauf si c'est le même)
                if new_username != user['username']:
                    for other_user in users:
                        if other_user['username'] == new_username:
                            return False, "Ce nom d'utilisateur est déjà utilisé"
                
                # Modifier les identifiants
                user['username'] = new_username
                user['password'] = self.hash_password(new_password)
                
                if self.save_all_users({'users': users}):
                    logger.info(f"Credentials modifiés pour le rôle {target_role}")
                    return True, "Identifiants modifiés avec succès"
                else:
                    return False, "Erreur lors de la sauvegarde"
        
        return False, f"Utilisateur avec le rôle {target_role} non trouvé"
    
    def get_users_list(self):
        """Retourne la liste des utilisateurs (sans les mots de passe)"""
        users = self.load_all_users()
        return [{'username': u['username'], 'role': u['role']} for u in users]
    
    @staticmethod
    def login_required(f):
        """Décorateur pour protéger les routes (admin uniquement)"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session or not session['logged_in']:
                if request.path.startswith('/api/'):
                    from flask import jsonify
                    return jsonify({'success': False, 'error': 'Non authentifié'}), 401
                return redirect(url_for('login'))
            # Vérifier que c'est un admin pour les routes admin
            if session.get('role') != 'admin':
                if request.path.startswith('/api/'):
                    from flask import jsonify
                    return jsonify({'success': False, 'error': 'Accès admin requis'}), 403
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    @staticmethod
    def any_login_required(f):
        """Décorateur pour protéger les routes (tout utilisateur connecté)"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session or not session['logged_in']:
                if request.path.startswith('/api/'):
                    from flask import jsonify
                    return jsonify({'success': False, 'error': 'Non authentifié'}), 401
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

# Instance globale
web_auth = WebAuth()

