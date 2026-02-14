# -*- coding: utf-8 -*-
"""
Module d'authentification pour le serveur web
Support multi-utilisateurs avec rôles (admin, user)
SÉCURITÉ: Utilise bcrypt pour le hachage des mots de passe
Stockage: SQLite (via src.database)
"""
import os
import json
import hashlib
from functools import wraps
from flask import session, redirect, url_for, request
from src.utils.logger import get_logger
from src.database import get_db_connection, init_db

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
    def __init__(self, json_config_file='web_users.json'):
        """Initialise le système d'authentification"""
        self.json_config_file = json_config_file
        
        # Initialiser la base de données
        init_db()
        
        # Migrer depuis le JSON si nécessaire
        self.ensure_users_exist()
    
    def ensure_users_exist(self):
        """Vérifie qu'il y a au moins un utilisateur, sinon crée les par défaut ou migre du JSON"""
        conn = get_db_connection()
        if not conn:
            return

        try:
            users = conn.execute('SELECT count(*) FROM users').fetchone()[0]
            
            if users == 0:
                # Si la base est vide, vérifier si on a un fichier JSON à migrer
                if os.path.exists(self.json_config_file):
                    self._migrate_from_json(conn)
                else:
                    self._create_default_users(conn)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des utilisateurs: {e}")
        finally:
            conn.close()
            
    def _create_default_users(self, conn):
        """Crée les utilisateurs par défaut"""
        logger.info("Création des utilisateurs par défaut...")
        try:
            default_users = [
                ('admin', self.hash_password('admin123'), 'admin', 1),
                ('user', self.hash_password('user123'), 'user', 1)
            ]
            conn.executemany('INSERT INTO users (username, password, role, must_change_password) VALUES (?, ?, ?, ?)', default_users)
            conn.commit()
            logger.warning("⚠️ SÉCURITÉ: Utilisateurs par défaut créés (admin/admin123, user/user123) - À CHANGER IMMÉDIATEMENT!")
        except Exception as e:
            logger.error(f"Erreur lors de la création des utilisateurs par défaut: {e}")

    def _migrate_from_json(self, conn):
        """Migre les utilisateurs depuis le fichier JSON"""
        logger.info(f"Migration des utilisateurs depuis {self.json_config_file}...")
        try:
            with open(self.json_config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            users_list = []
            
            # Format multi-utilisateurs
            if 'users' in data:
                for u in data['users']:
                    users_list.append((
                        u['username'],
                        u['password'],
                        u.get('role', 'user'),
                        u.get('must_change_password', False)
                    ))
            # Ancien format mono-utilisateur
            elif 'username' in data:
                 users_list.append((
                    data['username'],
                    data['password'],
                    'admin',
                    False
                ))
                 # Ajouter un user par défaut aussi
                 users_list.append(('user', self.hash_password('user123'), 'user', 1))

            if users_list:
                conn.executemany('INSERT INTO users (username, password, role, must_change_password) VALUES (?, ?, ?, ?)', users_list)
                conn.commit()
                logger.info("Migration JSON vers SQLite terminée avec succès.")
                
                # Renommer le fichier JSON pour éviter de le réutiliser
                os.rename(self.json_config_file, self.json_config_file + '.bak')
                logger.info(f"Fichier {self.json_config_file} renommé en .bak")
                
        except Exception as e:
            logger.error(f"Erreur lors de la migration JSON: {e}")

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
        """Charge tous les utilisateurs depuis la DB"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            users = conn.execute('SELECT * FROM users').fetchall()
            # Convertir sqlite3.Row en dict
            return [dict(u) for u in users]
        except Exception as e:
            logger.error(f"Erreur chargement users: {e}")
            return []
        finally:
            conn.close()

    def verify_credentials(self, username, password, client_ip=None):
        """Vérifie les identifiants et retourne le rôle si succès"""
        import time
        from datetime import datetime
        
        # Rate limiting basé sur l'IP
        if client_ip:
            current_time = time.time()
            if client_ip in _login_attempts:
                attempt_info = _login_attempts[client_ip]
                # Nettoyer si lockout expiré
                if current_time - attempt_info['last_attempt'] > LOGIN_LOCKOUT_TIME:
                    del _login_attempts[client_ip]
                elif attempt_info['count'] >= MAX_LOGIN_ATTEMPTS:
                    logger.warning(f"SÉCURITÉ: IP {client_ip} bloquée - trop de tentatives ({attempt_info['count']})")
                    return False, None, False
        
        conn = get_db_connection()
        if not conn:
            return False, None, False

        try:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
            if user and self.verify_password(password, user['password']):
                # Réinitialiser le compteur de tentatives
                if client_ip and client_ip in _login_attempts:
                    del _login_attempts[client_ip]
                
                # Mettre à jour last_login
                conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
                conn.commit()
                
                logger.info(f"Connexion réussie pour l'utilisateur: {username} (role: {user['role']})")
                return True, user['role'], bool(user['must_change_password'])
            
            # Échec
            # Incrémenter le compteur de tentatives échouées
            if client_ip:
                if client_ip not in _login_attempts:
                    _login_attempts[client_ip] = {'count': 0, 'last_attempt': 0}
                _login_attempts[client_ip]['count'] += 1
                _login_attempts[client_ip]['last_attempt'] = time.time()
                logger.warning(f"Tentative de connexion échouée pour: {username} depuis {client_ip}")
            else:
                logger.warning(f"Tentative de connexion échouée pour l'utilisateur: {username}")
                
            return False, None, False
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des identifiants: {e}")
            return False, None, False
        finally:
            conn.close()
    
    def change_credentials(self, old_password, new_username, new_password):
        """Change les identifiants admin (nécessite l'ancien mot de passe) - Obsolète pour legacy, mais gardons la logique"""
        conn = get_db_connection()
        if not conn:
             return False, "Erreur base de données"

        try:
            # Chercher un admin
            user = conn.execute("SELECT * FROM users WHERE role = 'admin' LIMIT 1").fetchone()
            
            if not user:
                return False, "Utilisateur admin non trouvé"
                
            if not self.verify_password(old_password, user['password']):
                return False, "Mot de passe actuel incorrect"
            
            # Vérifier si le nouveau nom existe déjà (si différent)
            if new_username != user['username']:
                exists = conn.execute('SELECT 1 FROM users WHERE username = ?', (new_username,)).fetchone()
                if exists:
                    return False, "Ce nom d'utilisateur est déjà utilisé"

            new_hash = self.hash_password(new_password)
            conn.execute('UPDATE users SET username = ?, password = ? WHERE id = ?', (new_username, new_hash, user['id']))
            conn.commit()
            
            return True, "Identifiants modifiés avec succès"
        except Exception as e:
            logger.error(f"Erreur changement credentials: {e}")
            return False, "Erreur lors de la modification"
        finally:
            conn.close()
    
    def change_user_credentials(self, target_role, new_username, new_password, current_password=None, current_username=None):
        """
        Change les identifiants d'un utilisateur par son rôle (legacy) ou username.
        Si current_username est fourni, on cible cet utilisateur spécifique.
        """
        conn = get_db_connection()
        if not conn:
             return False, "Erreur base de données"
             
        try:
            user = None
            if current_username:
                 user = conn.execute('SELECT * FROM users WHERE username = ?', (current_username,)).fetchone()
            else:
                 # Comportement legacy: prendre le premier du rôle
                 user = conn.execute('SELECT * FROM users WHERE role = ? LIMIT 1', (target_role,)).fetchone()
            
            if not user:
                return False, "Utilisateur non trouvé"

            # Vérification ancien mot de passe si fourni
            if current_password:
                if not self.verify_password(current_password, user['password']):
                    return False, "Mot de passe actuel incorrect"
            
            # Vérifier unicité username
            if new_username != user['username']:
                exists = conn.execute('SELECT 1 FROM users WHERE username = ?', (new_username,)).fetchone()
                if exists:
                    return False, "Ce nom d'utilisateur est déjà utilisé"

            new_hash = self.hash_password(new_password)
            conn.execute('UPDATE users SET username = ?, password = ?, must_change_password = 0 WHERE id = ?', (new_username, new_hash, user['id']))
            conn.commit()
            
            return True, "Identifiants modifiés avec succès"
        except Exception as e:
            logger.error(f"Erreur modification user: {e}")
            return False, "Erreur lors de la modification"
        finally:
            conn.close()
    
    def get_users_list(self):
        """Retourne la liste des utilisateurs (sans les mots de passe)"""
        conn = get_db_connection()
        if not conn:
            return []
            
        try:
            users = conn.execute('SELECT id, username, role, must_change_password, created_at, last_login FROM users').fetchall()
            return [dict(u) for u in users]
        except Exception as e:
            logger.error(f"Erreur liste utilisateurs: {e}")
            return []
        finally:
            conn.close()
    
    def add_user(self, username, password, role='user'):
        """Ajoute un nouvel utilisateur"""
        if role not in ['admin', 'user']:
            return False, "Rôle invalide"
            
        conn = get_db_connection()
        if not conn:
            return False, "Erreur base de données"
            
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                         (username, self.hash_password(password), role))
            conn.commit()
            logger.info(f"Nouvel utilisateur créé: {username} (role: {role})")
            return True, "Utilisateur créé avec succès"
        except sqlite3.IntegrityError:
            return False, "Ce nom d'utilisateur existe déjà"
        except Exception as e:
            logger.error(f"Erreur ajout utilisateur: {e}")
            return False, "Erreur lors de l'ajout"
        finally:
            conn.close()
    
    def delete_user(self, username):
        """Supprime un utilisateur"""
        conn = get_db_connection()
        if not conn:
            return False, "Erreur base de données"
            
        try:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if not user:
                return False, "Utilisateur non trouvé"
            
            # Protection dernier admin
            if user['role'] == 'admin':
                admin_count = conn.execute("SELECT count(*) FROM users WHERE role = 'admin'").fetchone()[0]
                if admin_count <= 1:
                    return False, "Impossible de supprimer le dernier administrateur"

            conn.execute('DELETE FROM users WHERE id = ?', (user['id'],))
            conn.commit()
            logger.info(f"Utilisateur supprimé: {username}")
            return True, "Utilisateur supprimé avec succès"
        except Exception as e:
            logger.error(f"Erreur suppression utilisateur: {e}")
            return False, "Erreur lors de la suppression"
        finally:
            conn.close()
    
    def update_user_password(self, username, new_password):
        """Met à jour le mot de passe d'un utilisateur (admin uniquement)"""
        conn = get_db_connection()
        if not conn:
            return False, "Erreur base de données"
            
        try:
            user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if not user:
                return False, "Utilisateur non trouvé"
                
            new_hash = self.hash_password(new_password)
            conn.execute('UPDATE users SET password = ? WHERE id = ?', (new_hash, user['id']))
            conn.commit()
            logger.info(f"Mot de passe réinitialisé pour: {username}")
            return True, "Mot de passe modifié avec succès"
        except Exception as e:
            logger.error(f"Erreur update password: {e}")
            return False, "Erreur lors de la modification"
        finally:
            conn.close()
            
    def update_user_role(self, username, new_role):
        """Met à jour le rôle d'un utilisateur"""
        if new_role not in ['admin', 'user']:
            return False, "Rôle invalide"
            
        conn = get_db_connection()
        if not conn:
            return False, "Erreur base de données"
            
        try:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if not user:
                return False, "Utilisateur non trouvé"
            
            old_role = user['role']
            if old_role == 'admin' and new_role == 'user':
                admin_count = conn.execute("SELECT count(*) FROM users WHERE role = 'admin'").fetchone()[0]
                if admin_count <= 1:
                    return False, "Impossible de retirer le rôle du dernier administrateur"
            
            conn.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user['id']))
            conn.commit()
            logger.info(f"Rôle modifié pour {username}: {old_role} -> {new_role}")
            return True, "Rôle modifié avec succès"
        except Exception as e:
            logger.error(f"Erreur update role: {e}")
            return False, "Erreur lors de la modification"
        finally:
            conn.close()

    @staticmethod
    def login_required(f):
        """Décorateur pour protéger les routes (admin uniquement)"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session or not session['logged_in']:
                if request.path.startswith('/api/'):
                    from flask import jsonify
                    return jsonify({'success': False, 'error': 'Non authentifié'}), 401
                return redirect(url_for('auth.login'))
            # Vérifier que c'est un admin pour les routes admin
            if session.get('role') != 'admin':
                if request.path.startswith('/api/'):
                    from flask import jsonify
                    return jsonify({'success': False, 'error': 'Accès admin requis'}), 403
                return redirect(url_for('main.index'))
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
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function

# Instance globale
web_auth = WebAuth()

