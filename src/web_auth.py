# -*- coding: utf-8 -*-
"""
Module d'authentification pour le serveur web
Support multi-utilisateurs avec rôles (admin, user)
SÉCURITÉ: Utilise bcrypt pour le hachage des mots de passe
"""
import os
import json
import hashlib
from functools import wraps
from flask import session, redirect, url_for, request
from src.utils.logger import get_logger

# Essayer d'importer bcrypt pour un hachage sécurisé
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False

logger = get_logger(__name__)

# Compteur de tentatives de connexion pour rate limiting simple
_login_attempts = {}  # {ip: {'count': n, 'last_attempt': timestamp}}
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_TIME = 300  # 5 minutes

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
                        'password': self.hash_password('admin123'),  # Mot de passe par défaut plus fort
                        'role': 'admin',
                        'must_change_password': True  # Forcer le changement au premier login
                    },
                    {
                        'username': 'user',
                        'password': self.hash_password('user123'),
                        'role': 'user',
                        'must_change_password': True
                    }
                ]
            }
            self.save_all_users(default_users)
            logger.warning("⚠️ SÉCURITÉ: Fichier créé avec mots de passe par défaut (admin/admin123, user/user123) - À CHANGER IMMÉDIATEMENT!")
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
                            'password': self.hash_password('user123'),
                            'role': 'user',
                            'must_change_password': True
                        }
                    ]
                }
                self.save_all_users(new_data)
                logger.info("Migration terminée")
        except Exception as e:
            logger.error(f"Erreur lors de la migration: {e}")
    
    def hash_password(self, password):
        """Hash un mot de passe avec bcrypt (si disponible) ou SHA256"""
        if BCRYPT_AVAILABLE:
            # bcrypt avec coût de 12 (bon équilibre sécurité/performance)
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
        else:
            # Fallback SHA256 (moins sécurisé mais fonctionne partout)
            logger.warning("bcrypt non disponible, utilisation de SHA256 (moins sécurisé)")
            return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def verify_password(self, password, hashed):
        """Vérifie un mot de passe contre son hash"""
        if BCRYPT_AVAILABLE and hashed.startswith('$2'):
            # Hash bcrypt
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        else:
            # Fallback SHA256 pour compatibilité avec anciens hash
            return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed
    
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
                {'username': 'admin', 'password': self.hash_password('admin123'), 'role': 'admin'},
                {'username': 'user', 'password': self.hash_password('user123'), 'role': 'user'}
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
        return {'username': 'admin', 'password': self.hash_password('admin123'), 'role': 'admin'}
    
    def save_credentials(self, username, password_hash):
        """Sauvegarde les identifiants admin (compatibilité)"""
        users = self.load_all_users()
        for user in users:
            if user.get('role') == 'admin':
                user['username'] = username
                user['password'] = password_hash
                break
        return self.save_all_users({'users': users})
    
    def verify_credentials(self, username, password, client_ip=None):
        """Vérifie les identifiants et retourne le rôle si succès
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe en clair
            client_ip: IP du client pour rate limiting (optionnel)
        
        Returns:
            tuple: (success: bool, role: str|None, must_change: bool)
        """
        import time
        
        # Rate limiting basé sur l'IP
        if client_ip:
            current_time = time.time()
            if client_ip in _login_attempts:
                attempt_info = _login_attempts[client_ip]
                # Nettoyer si lockout expiré
                if current_time - attempt_info['last_attempt'] > LOGIN_LOCKOUT_TIME:
                    del _login_attempts[client_ip]
                elif attempt_info['count'] >= MAX_LOGIN_ATTEMPTS:
                    remaining = int(LOGIN_LOCKOUT_TIME - (current_time - attempt_info['last_attempt']))
                    logger.warning(f"SÉCURITÉ: IP {client_ip} bloquée - trop de tentatives ({attempt_info['count']})")
                    return False, None, False
        
        users = self.load_all_users()
        
        for user in users:
            if user['username'] == username:
                # Utiliser verify_password pour compatibilité bcrypt/SHA256
                if self.verify_password(password, user['password']):
                    # Réinitialiser le compteur de tentatives
                    if client_ip and client_ip in _login_attempts:
                        del _login_attempts[client_ip]
                    
                    must_change = user.get('must_change_password', False)
                    logger.info(f"Connexion réussie pour l'utilisateur: {username} (role: {user.get('role', 'user')})")
                    return True, user.get('role', 'user'), must_change
        
        # Incrémenter le compteur de tentatives échouées
        if client_ip:
            if client_ip not in _login_attempts:
                _login_attempts[client_ip] = {'count': 0, 'last_attempt': 0}
            _login_attempts[client_ip]['count'] += 1
            _login_attempts[client_ip]['last_attempt'] = time.time()
            logger.warning(f"Tentative de connexion échouée pour: {username} depuis {client_ip} (tentative {_login_attempts[client_ip]['count']}/{MAX_LOGIN_ATTEMPTS})")
        else:
            logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {username}")
        
        return False, None, False
    
    def change_credentials(self, old_password, new_username, new_password):
        """Change les identifiants admin (nécessite l'ancien mot de passe)"""
        users = self.load_all_users()
        old_password_hash = self.hash_password(old_password)
        
        # Trouver l'admin
        for user in users:
            if user.get('role') == 'admin':
                if not self.verify_password(old_password, user['password']):
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
    
    def add_user(self, username, password, role='user'):
        """Ajoute un nouvel utilisateur"""
        users = self.load_all_users()
        
        # Vérifier que le username n'existe pas déjà
        for user in users:
            if user['username'] == username:
                return False, "Ce nom d'utilisateur existe déjà"
        
        # Valider le rôle
        if role not in ['admin', 'user']:
            role = 'user'
        
        # Ajouter l'utilisateur
        new_user = {
            'username': username,
            'password': self.hash_password(password),
            'role': role
        }
        users.append(new_user)
        
        if self.save_all_users({'users': users}):
            logger.info(f"Nouvel utilisateur créé: {username} (role: {role})")
            return True, "Utilisateur créé avec succès"
        else:
            return False, "Erreur lors de la sauvegarde"
    
    def delete_user(self, username):
        """Supprime un utilisateur (ne peut pas supprimer le dernier admin)"""
        users = self.load_all_users()
        
        # Trouver l'utilisateur à supprimer
        user_to_delete = None
        for user in users:
            if user['username'] == username:
                user_to_delete = user
                break
        
        if not user_to_delete:
            return False, "Utilisateur non trouvé"
        
        # Ne pas permettre de supprimer le dernier admin
        if user_to_delete['role'] == 'admin':
            admin_count = sum(1 for u in users if u['role'] == 'admin')
            if admin_count <= 1:
                return False, "Impossible de supprimer le dernier administrateur"
        
        # Supprimer l'utilisateur
        users = [u for u in users if u['username'] != username]
        
        if self.save_all_users({'users': users}):
            logger.info(f"Utilisateur supprimé: {username}")
            return True, "Utilisateur supprimé avec succès"
        else:
            return False, "Erreur lors de la sauvegarde"
    
    def update_user_password(self, username, new_password):
        """Met à jour le mot de passe d'un utilisateur (admin uniquement)"""
        users = self.load_all_users()
        
        for user in users:
            if user['username'] == username:
                user['password'] = self.hash_password(new_password)
                
                if self.save_all_users({'users': users}):
                    logger.info(f"Mot de passe modifié pour: {username}")
                    return True, "Mot de passe modifié avec succès"
                else:
                    return False, "Erreur lors de la sauvegarde"
        
        return False, "Utilisateur non trouvé"
    
    def update_user_role(self, username, new_role):
        """Met à jour le rôle d'un utilisateur"""
        users = self.load_all_users()
        
        if new_role not in ['admin', 'user']:
            return False, "Rôle invalide"
        
        for user in users:
            if user['username'] == username:
                old_role = user['role']
                
                # Ne pas permettre de retirer le dernier admin
                if old_role == 'admin' and new_role == 'user':
                    admin_count = sum(1 for u in users if u['role'] == 'admin')
                    if admin_count <= 1:
                        return False, "Impossible de retirer le rôle du dernier administrateur"
                
                user['role'] = new_role
                
                if self.save_all_users({'users': users}):
                    logger.info(f"Rôle modifié pour {username}: {old_role} -> {new_role}")
                    return True, "Rôle modifié avec succès"
                else:
                    return False, "Erreur lors de la sauvegarde"
        
        return False, "Utilisateur non trouvé"
    
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

