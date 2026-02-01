# -*- coding: utf-8 -*-
"""
Serveur Web pour afficher les hôtes monitorés en temps réel
Utilise Flask et Socket.IO pour les mises à jour automatiques
"""
import socket
import asyncio
import secrets
import logging
import threading

try:
    from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for, send_from_directory
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS
    import json
    import shutil
    import os
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    class Flask: 
        def __init__(self, *args, **kwargs): pass
        def route(self, *args, **kwargs): return lambda f: f
        def config(self): return {}
    class SocketIO: 
        def __init__(self, *args, **kwargs): pass
        def on(self, *args, **kwargs): return lambda f: f
        def run(self, *args, **kwargs): pass
    def jsonify(*args, **kwargs): return {}
    def render_template(*args, **kwargs): return ""
    def request(*args, **kwargs): return None
    def session(*args, **kwargs): return {}
    def redirect(*args, **kwargs): return ""
    def url_for(*args, **kwargs): return ""
    def CORS(*args, **kwargs): pass

try:
    from PySide6.QtCore import QObject, Signal
    from PySide6.QtGui import QStandardItem
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    class QObject: pass
    class Signal: 
        def __init__(self, *args): pass
        def emit(self, *args): pass
        def connect(self, *args): pass
    class QStandardItem:
        def __init__(self, text=""): self._text = text
        def text(self): return self._text

from src.utils.logger import get_logger
from src.utils.colors import format_bandwidth
from src.web_auth import web_auth, WebAuth

logger = get_logger(__name__)

# Import optionnel de SNMP
try:
    from src.utils.snmp_helper import snmp_helper
    SNMP_AVAILABLE = True
except ImportError as e:
    logger.warning(f"SNMP non disponible pour le serveur web: {e}")
    snmp_helper = None
    SNMP_AVAILABLE = False

# Import du scanner réseau
try:
    from src.utils.network_scanner import NetworkScanner
    NETWORK_SCANNER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Network scanner non disponible: {e}")
    NetworkScanner = None
    NETWORK_SCANNER_AVAILABLE = False


class WebServer(QObject):
    """Serveur Web Flask avec Socket.IO pour diffusion en temps réel"""
    
    data_updated = Signal(dict)
    
    def __init__(self, main_window, port=9090):
        super().__init__()
        self.main_window = main_window
        self.port = port
        
        # Déterminer le chemin absolu des templates
        import os
        import sys
        if getattr(sys, 'frozen', False):
            # Mode PyInstaller - les fichiers sont copiés dans src/web/templates
            base_path = sys._MEIPASS
            template_path = os.path.join(base_path, 'src', 'web', 'templates')
            static_path = os.path.join(base_path, 'src', 'web', 'static')
        else:
            # Mode développement
            base_path = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(base_path, 'web', 'templates')
            static_path = os.path.join(base_path, 'web', 'static')
        
        # Log des chemins utilisés pour le débogage
        logger.info(f"Mode frozen: {getattr(sys, 'frozen', False)}")
        logger.info(f"Template path: {template_path}")
        logger.info(f"Static path: {static_path}")
        logger.info(f"Template path exists: {os.path.exists(template_path)}")
        if os.path.exists(template_path):
            logger.info(f"Files in template path: {os.listdir(template_path)}")
        
        self.app = Flask(__name__, 
                        template_folder=template_path,
                        static_folder=static_path)
        
        # Configuration de la session
        self.app.config['SECRET_KEY'] = secrets.token_hex(32)
        self.app.config['SESSION_COOKIE_SECURE'] = False  # True si HTTPS
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        
        CORS(self.app)
        
        # ═══════════════════════════════════════════════════════════════
        # ⚠️ NE JAMAIS RETIRER async_mode='threading' ⚠️
        # C'est OBLIGATOIRE pour que Socket.IO fonctionne dans PyInstaller
        # Sans ce paramètre → Erreur : "Invalid async_mode specified"
        # ═══════════════════════════════════════════════════════════════
        # NOTE: CORS ouvert (*) pour accès réseau - Sécurité assurée par authentification
        self.socketio = SocketIO(self.app, 
                                cors_allowed_origins="*",
                                async_mode='threading',  # ← NE JAMAIS RETIRER !
                                logger=False,
                                engineio_logger=False,
                                # Paramètres pour éviter les erreurs de timeout
                                ping_timeout=60,
                                ping_interval=25,
                                # Réessayer automatiquement en cas d'échec
                                max_http_buffer_size=1000000)
        self.server_thread = None
        self.running = False
        
        # Cache partagé pour les débits SNMP (référence au cache du PingManager)
        self.traffic_cache = {}
        self._bandwidth_cache = {}  # Cache des derniers débits calculés (IP -> {in_mbps, out_mbps})
        
        # Network scanner
        self._network_scanner = None
        self._scan_thread = None
        if NETWORK_SCANNER_AVAILABLE:
            self._network_scanner = NetworkScanner()
            self._network_scanner.add_callback(self._on_device_discovered)
        
        self._setup_routes()
        self._setup_socketio()
        
    def _setup_routes(self):
        """Configuration des routes Flask"""
        
        @self.app.route('/')
        @WebAuth.any_login_required
        def index():
            try:
                # Passer le rôle au template pour afficher le lien admin si nécessaire
                is_admin = session.get('role') == 'admin'
                username = session.get('username', '')
                return render_template('index.html', is_admin=is_admin, username=username)
            except Exception as e:
                logger.error(f"Erreur lors du rendu du template: {e}", exc_info=True)
                # Retourner une réponse JSON en cas d'erreur pour éviter write() before start_response
                return jsonify({'error': 'Template introuvable', 'message': str(e)}), 500
        
        @self.app.route('/test')
        def test_page():
            try:
                return render_template('test_simple.html')
            except Exception as e:
                logger.error(f"Erreur lors du rendu du template de test: {e}", exc_info=True)
                return jsonify({'error': 'Template introuvable', 'message': str(e)}), 500
        
        @self.app.route('/api/hosts')
        def get_hosts():
            # Pour l'API web, on retourne toujours tous les hôtes 
            # et on laisse le frontend gérer son propre filtrage
            hosts = self._get_hosts_data(apply_filter=False)
            return jsonify(hosts)
        
        @self.app.route('/api/local_ip')
        @WebAuth.login_required
        def get_local_ip():
            try:
                # Créer une socket dummy pour trouver l'IP routable vvers l'extérieur
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    # N'a pas besoin d'être atteignable
                    s.connect(('10.255.255.255', 1))
                    IP = s.getsockname()[0]
                except Exception:
                    IP = '127.0.0.1'
                finally:
                    s.close()
                
                return jsonify({'success': True, 'ip': IP})
            except Exception as e:
                logger.error(f"Erreur récupération IP locale: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/status')
        def status():
            return jsonify({
                'status': 'running',
                'hosts_count': self._get_hosts_count()
            })
        
        @self.app.route('/login', methods=['GET'])
        def login():
            try:
                # Si déjà connecté, rediriger vers la page appropriée
                if session.get('logged_in'):
                    if session.get('role') == 'admin':
                        return redirect(url_for('admin'))
                    else:
                        return redirect(url_for('index'))
                return render_template('login.html')
            except Exception as e:
                logger.error(f"Erreur lors du rendu du template login: {e}", exc_info=True)
                return jsonify({'error': 'Template introuvable', 'message': str(e)}), 500
        
        @self.app.route('/api/login', methods=['POST'])
        def api_login():
            try:
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                
                # Récupérer l'IP client pour le rate limiting
                client_ip = request.remote_addr
                
                success, role, must_change = web_auth.verify_credentials(username, password, client_ip)
                if success:
                    session['logged_in'] = True
                    session['username'] = username
                    session['role'] = role
                    logger.info(f"Connexion réussie: {username} (role: {role})")
                    # Indiquer si c'est un admin et si changement de mot de passe requis
                    return jsonify({
                        'success': True, 
                        'message': 'Connexion réussie', 
                        'role': role,
                        'must_change_password': must_change
                    })
                else:
                    # Message générique pour ne pas révéler si l'utilisateur existe
                    return jsonify({'success': False, 'error': 'Identifiants incorrects ou compte bloqué'}), 401
            except Exception as e:
                logger.error(f"Erreur login: {e}", exc_info=True)
                # Message générique en production
                return jsonify({'success': False, 'error': 'Erreur de connexion'}), 500
        
        @self.app.route('/api/logout', methods=['POST'])
        def api_logout():
            try:
                username = session.get('username', 'unknown')
                session.clear()
                logger.info(f"Déconnexion: {username}")
                return jsonify({'success': True, 'message': 'Déconnexion réussie'})
            except Exception as e:
                logger.error(f"Erreur logout: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/update_comment', methods=['POST'])
        @WebAuth.any_login_required
        def update_comment():
            try:
                data = request.get_json()
                ip = data.get('ip')
                comment = data.get('comment')
                
                if not ip:
                    return jsonify({'success': False, 'error': 'IP requise'}), 400
                
                # Mettre à jour dans le modèle
                model = self.main_window.treeIpModel
                for row in range(model.rowCount()):
                    item_ip = model.item(row, 1)
                    if item_ip and item_ip.text() == ip:
                        comment_item = QStandardItem(comment)
                        model.setItem(row, 9, comment_item)
                        # Notifier d'une mise à jour (diffusion socket.io)
                        self.socketio.emit('hosts_update', self._get_hosts_data())
                        return jsonify({'success': True})
                
                return jsonify({'success': False, 'error': 'IP non trouvée'}), 404
            except Exception as e:
                logger.error(f"Erreur update_comment: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/user_info')
        @WebAuth.any_login_required
        def user_info():
            """Retourne les informations de l'utilisateur connecté"""
            return jsonify({
                'success': True,
                'username': session.get('username', ''),
                'role': session.get('role', 'user'),
                'is_admin': session.get('role') == 'admin'
            })
        
        @self.app.route('/admin')
        @WebAuth.login_required
        def admin():
            try:
                return render_template('admin.html')
            except Exception as e:
                logger.error(f"Erreur lors du rendu du template admin: {e}", exc_info=True)
                return jsonify({'error': 'Template introuvable', 'message': str(e)}), 500
        
        @self.app.route('/api/change_credentials', methods=['POST'])
        @WebAuth.login_required
        def change_credentials():
            try:
                data = request.get_json()
                old_password = data.get('old_password')
                new_username = data.get('new_username')
                new_password = data.get('new_password')
                
                if not all([old_password, new_username, new_password]):
                    return jsonify({'success': False, 'error': 'Tous les champs sont requis'}), 400
                
                success, message = web_auth.change_credentials(old_password, new_username, new_password)
                
                if success:
                    # Déconnecter l'utilisateur pour qu'il se reconnecte avec les nouveaux identifiants
                    session.clear()
                    return jsonify({'success': True, 'message': message})
                else:
                    return jsonify({'success': False, 'error': message}), 400
            except Exception as e:
                logger.error(f"Erreur changement credentials: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/get_users')
        @WebAuth.login_required
        def get_users():
            """Récupère la liste des utilisateurs (admin only)"""
            try:
                users = web_auth.get_users_list()
                return jsonify({'success': True, 'users': users})
            except Exception as e:
                logger.error(f"Erreur récupération utilisateurs: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/change_user_credentials', methods=['POST'])
        @WebAuth.login_required
        def change_user_credentials():
            """Change les identifiants d'un utilisateur (admin only)"""
            try:
                data = request.get_json()
                target_role = data.get('role')
                new_username = data.get('new_username')
                new_password = data.get('new_password')
                
                if not all([target_role, new_username, new_password]):
                    return jsonify({'success': False, 'error': 'Tous les champs sont requis'}), 400
                
                # Admin peut changer les credentials de n'importe quel utilisateur sans mot de passe
                success, message = web_auth.change_user_credentials(
                    target_role, 
                    new_username, 
                    new_password
                )
                
                if success:
                    return jsonify({'success': True, 'message': message})
                else:
                    return jsonify({'success': False, 'error': message}), 400
            except Exception as e:
                logger.error(f"Erreur changement credentials utilisateur: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/add_user', methods=['POST'])
        @WebAuth.login_required
        def add_user():
            """Ajoute un nouvel utilisateur (admin only)"""
            try:
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                role = data.get('role', 'user')
                
                if not all([username, password]):
                    return jsonify({'success': False, 'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
                
                success, message = web_auth.add_user(username, password, role)
                
                if success:
                    return jsonify({'success': True, 'message': message})
                else:
                    return jsonify({'success': False, 'error': message}), 400
            except Exception as e:
                logger.error(f"Erreur ajout utilisateur: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/delete_user', methods=['POST'])
        @WebAuth.login_required
        def delete_user():
            """Supprime un utilisateur (admin only)"""
            try:
                data = request.get_json()
                username = data.get('username')
                
                if not username:
                    return jsonify({'success': False, 'error': 'Nom d\'utilisateur requis'}), 400
                
                # Ne pas permettre de se supprimer soi-même
                if username == session.get('username'):
                    return jsonify({'success': False, 'error': 'Vous ne pouvez pas vous supprimer vous-même'}), 400
                
                success, message = web_auth.delete_user(username)
                
                if success:
                    return jsonify({'success': True, 'message': message})
                else:
                    return jsonify({'success': False, 'error': message}), 400
            except Exception as e:
                logger.error(f"Erreur suppression utilisateur: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/update_user_password', methods=['POST'])
        @WebAuth.login_required
        def update_user_password():
            """Met à jour le mot de passe d'un utilisateur (admin only)"""
            try:
                data = request.get_json()
                username = data.get('username')
                new_password = data.get('new_password')
                
                if not all([username, new_password]):
                    return jsonify({'success': False, 'error': 'Nom d\'utilisateur et nouveau mot de passe requis'}), 400
                
                success, message = web_auth.update_user_password(username, new_password)
                
                if success:
                    return jsonify({'success': True, 'message': message})
                else:
                    return jsonify({'success': False, 'error': message}), 400
            except Exception as e:
                logger.error(f"Erreur mise à jour mot de passe: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/update_user_role', methods=['POST'])
        @WebAuth.login_required
        def update_user_role():
            """Met à jour le rôle d'un utilisateur (admin only)"""
            try:
                data = request.get_json()
                username = data.get('username')
                new_role = data.get('role')
                
                if not all([username, new_role]):
                    return jsonify({'success': False, 'error': 'Nom d\'utilisateur et rôle requis'}), 400
                
                # Ne pas permettre de changer son propre rôle
                if username == session.get('username'):
                    return jsonify({'success': False, 'error': 'Vous ne pouvez pas changer votre propre rôle'}), 400
                
                success, message = web_auth.update_user_role(username, new_role)
                
                if success:
                    return jsonify({'success': True, 'message': message})
                else:
                    return jsonify({'success': False, 'error': message}), 400
            except Exception as e:
                logger.error(f"Erreur mise à jour rôle: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/add_hosts', methods=['POST'])
        @WebAuth.login_required
        def add_hosts():
            try:
                data = request.get_json()
                ip = data.get('ip', '').strip()
                hosts = data.get('hosts', 1)
                port = data.get('port', '80')
                scan_type = data.get('scan_type', 'alive')
                site = data.get('site', '')  # Site à assigner aux hôtes scannés
                
                # SÉCURITÉ: Validation de l'IP ou de l'URL
                is_valid = False
                is_url = False
                
                # Vérifier si c'est une URL (site web)
                if ip.startswith('http://') or ip.startswith('https://') or any(c.isalpha() for c in ip):
                    # C'est probablement une URL/domaine
                    # Validation basique: pas vide et contient au moins un point ou commence par http
                    if ip and (('.' in ip) or ip.startswith('http')):
                        is_valid = True
                        is_url = True
                        logger.info(f"URL/Domaine détecté pour monitoring: {ip}")
                else:
                    # C'est probablement une IP, valider strictement
                    try:
                        from src import secure_config
                        if secure_config.validate_ip(ip):
                            is_valid = True
                    except ImportError:
                        # Fallback de validation basique pour IP
                        import re
                        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
                            is_valid = True
                
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Adresse IP ou URL invalide'}), 400
                
                # Validation du nombre d'hôtes
                try:
                    hosts = int(hosts)
                    if hosts < 1 or hosts > 255:
                        return jsonify({'success': False, 'error': 'Nombre d\'hôtes invalide (1-255)'}), 400
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'error': 'Nombre d\'hôtes invalide'}), 400
                
                # Validation du port
                try:
                    port_int = int(port)
                    if port_int < 1 or port_int > 65535:
                        return jsonify({'success': False, 'error': 'Port invalide (1-65535)'}), 400
                except (ValueError, TypeError):
                    return jsonify({'success': False, 'error': 'Port invalide'}), 400
                
                # Lancer le scan dans un thread séparé
                import threading
                from src import threadAjIp
                
                thread = threading.Thread(
                    target=threadAjIp.main,
                    args=(self.main_window, self.main_window.comm, 
                          self.main_window.treeIpModel, ip, hosts, 
                          scan_type.capitalize(), str(port), "", site)
                )
                thread.start()
                
                site_info = f" (site: {site})" if site else ""
                logger.info(f"Scan d'hôtes démarré: {ip}, {hosts} hôtes, type: {scan_type}{site_info}")
                return jsonify({'success': True, 'message': f'Scan de {hosts} hôte(s) démarré'})
            except Exception as e:
                logger.error(f"Erreur ajout hôtes: {e}", exc_info=True)
                return jsonify({'success': False, 'error': 'Erreur lors du scan'}), 500
        
        @self.app.route('/api/start_monitoring', methods=['POST'])
        @WebAuth.login_required
        def start_monitoring():
            try:
                data = request.get_json()
                delai = data.get('delai', 10)
                nb_hs = data.get('nb_hs', 3)
                
                # Mettre à jour les variables
                from src import var
                var.delais = delai
                var.nbrHs = int(nb_hs)  # Force int conversion
                
                # Démarrer le monitoring via le contrôleur (thread-safe avec signal Qt)
                if hasattr(self.main_window, 'main_controller'):
                    # Vérifier si le monitoring est déjà en cours (ping_manager existe)
                    if self.main_window.main_controller.ping_manager is None:
                        # Mise à jour des variables AVANT de démarrer
                        logger.info(f"Configuration reçue: Délai={delai}s, Nb HS={nb_hs}")
                        
                        # Utiliser un signal Qt pour démarrer le monitoring de manière thread-safe
                        self.main_window.comm.start_monitoring_signal.emit()
                        logger.info(f"Monitoring démarré via API (délai: {delai}s, nb_hs: {nb_hs})")
                        # Notifier tous les clients
                        self.socketio.emit('monitoring_status', {'running': True}, namespace='/')
                        return jsonify({'success': True, 'message': 'Monitoring démarré'})
                    else:
                        # Monitoring déjà en cours, mais on met à jour les paramètres
                        # et on nettoie les listes pour éviter les fausses alertes
                        logger.info(f"Mise à jour configuration: Délai={delai}s, Nb HS={nb_hs}")
                        self._clean_alert_lists_for_new_threshold(int(nb_hs))
                        return jsonify({'success': True, 'message': 'Configuration mise à jour'})
                
                return jsonify({'success': False, 'error': 'Contrôleur non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur démarrage monitoring: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stop_monitoring', methods=['POST'])
        @WebAuth.login_required
        def stop_monitoring():
            try:
                if hasattr(self.main_window, 'main_controller'):
                    # Vérifier si le monitoring est en cours (ping_manager existe)
                    if self.main_window.main_controller.ping_manager is not None:
                        # Utiliser un signal Qt pour arrêter le monitoring de manière thread-safe
                        self.main_window.comm.stop_monitoring_signal.emit()
                        logger.info("Monitoring arrêté via API")
                        # Notifier tous les clients
                        self.socketio.emit('monitoring_status', {'running': False}, namespace='/')
                        return jsonify({'success': True, 'message': 'Monitoring arrêté'})
                    else:
                        return jsonify({'success': True, 'message': 'Monitoring déjà arrêté'})
                
                return jsonify({'success': False, 'error': 'Contrôleur non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur arrêt monitoring: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/save_alerts', methods=['POST'])
        @WebAuth.login_required
        def save_alerts():
            try:
                data = request.get_json()
                from src import var, db
                
                var.popup = data.get('popup', False)
                var.mail = data.get('mail', False)
                var.telegram = data.get('telegram', False)
                var.mailRecap = data.get('mail_recap', False)
                var.dbExterne = data.get('db_externe', False)
                var.tempAlert = data.get('temp_alert', False)
                var.tempSeuil = data.get('temp_seuil', 70)
                var.tempSeuilWarning = data.get('temp_seuil_warning', 60)
                
                # Sauvegarder dans le fichier de configuration
                db.save_param_db()
                
                logger.info(f"Alertes sauvegardées via API: {data}")
                return jsonify({'success': True, 'message': 'Alertes sauvegardées'})
            except Exception as e:
                logger.error(f"Erreur sauvegarde alertes: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/clear_all', methods=['POST'])
        @WebAuth.login_required
        def clear_all():
            try:
                model = self.main_window.treeIpModel
                count_before = model.rowCount()
                
                # Utiliser clear() si disponible, sinon removeRows
                if hasattr(model, 'clear'):
                    model.clear()
                    model.setHorizontalHeaderLabels([
                        "Id", "IP", "Nom", "Mac", "Port", "Latence", "Temp", "Suivi", "site", "Commentaire", "Excl"
                    ])
                else:
                    for i in range(count_before - 1, -1, -1):
                        model.removeRow(i)
                
                # Vider aussi les listes d'alertes
                from src import var
                var.liste_hs.clear()
                var.liste_mail.clear()
                var.liste_telegram.clear()
                
                # Sauvegarde immédiate sur disque
                try:
                    import os
                    from src import fct
                    autosave_path = os.path.join("bd", "autosave.pin")
                    # Passer None comme 'self' car fct.save_csv n'utilise self que pour GUI/tr si silent=False
                    fct.save_csv(None, model, filepath=autosave_path, silent=True)
                except Exception as e:
                    logger.error(f"Erreur lors de la sauvegarde post-suppression : {e}")

                logger.info(f"{count_before} hôtes supprimés")
                
                self.broadcast_update()
                return jsonify({'success': True, 'message': f'{count_before} hôtes supprimés'})
            except Exception as e:
                logger.error(f"Erreur suppression tous les hôtes: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/remove_duplicates', methods=['POST'])
        @WebAuth.login_required
        def remove_duplicates():
            """Supprime les doublons d'IP du modèle"""
            try:
                from src import fct
                model = self.main_window.treeIpModel
                count_before = model.rowCount()
                
                duplicates_removed = fct.remove_duplicates_from_model(model)
                count_after = model.rowCount()
                
                if duplicates_removed > 0:
                    logger.info(f"{duplicates_removed} doublon(s) supprimé(s)")
                
                self.broadcast_update()
                return jsonify({
                    'success': True, 
                    'message': f'{duplicates_removed} doublon(s) supprimé(s)',
                    'duplicates_removed': duplicates_removed,
                    'hosts_before': count_before,
                    'hosts_after': count_after
                })
            except Exception as e:
                logger.error(f"Erreur suppression doublons: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/delete_host', methods=['POST'])
        @WebAuth.login_required
        def delete_host():
            try:
                data = request.get_json()
                ip = data.get('ip')
                
                model = self.main_window.treeIpModel
                for row in range(model.rowCount()):
                    item = model.item(row, 1)  # Colonne IP
                    if item and item.text() == ip:
                        model.removeRow(row)
                        logger.info(f"Hôte {ip} supprimé via API")
                        self.broadcast_update()
                        return jsonify({'success': True, 'message': f'Hôte {ip} supprimé'})
                
                return jsonify({'success': False, 'error': 'Hôte non trouvé'}), 404
            except Exception as e:
                logger.error(f"Erreur suppression hôte: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/exclude_host', methods=['POST'])
        @WebAuth.login_required
        def exclude_host():
            try:
                data = request.get_json()
                ip = data.get('ip')
                
                # Import QStandardItem selon le mode
                if GUI_AVAILABLE:
                    from PySide6.QtGui import QStandardItem
                else:
                    QStandardItem = type('QStandardItem', (), {
                        '__init__': lambda self, text="": setattr(self, '_text', str(text)),
                        'text': lambda self: self._text,
                        'setText': lambda self, t: setattr(self, '_text', str(t))
                    })
                
                model = self.main_window.treeIpModel
                for row in range(model.rowCount()):
                    item_ip = model.item(row, 1)  # Colonne IP
                    if item_ip and item_ip.text() == ip:
                        excl_item = QStandardItem("x")
                        model.setItem(row, 10, excl_item)  # Colonne Excl
                        
                        # Réinitialiser le statut visuel
                        latence_item = model.item(row, 5)
                        if latence_item:
                            latence_item.setText("EXCLU")
                        
                        logger.info(f"Hôte {ip} exclu via API")
                        self.broadcast_update()
                        return jsonify({'success': True, 'message': f'Hôte {ip} exclu'})
                
                return jsonify({'success': False, 'error': 'Hôte non trouvé'}), 404
            except Exception as e:
                logger.error(f"Erreur exclusion hôte: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/include_host', methods=['POST'])
        @WebAuth.login_required
        def include_host():
            try:
                data = request.get_json()
                ip = data.get('ip')
                
                # Import QStandardItem selon le mode
                if GUI_AVAILABLE:
                    from PySide6.QtGui import QStandardItem
                else:
                    QStandardItem = type('QStandardItem', (), {
                        '__init__': lambda self, text="": setattr(self, '_text', str(text)),
                        'text': lambda self: self._text,
                        'setText': lambda self, t: setattr(self, '_text', str(t))
                    })
                
                model = self.main_window.treeIpModel
                for row in range(model.rowCount()):
                    item_ip = model.item(row, 1)  # Colonne IP
                    if item_ip and item_ip.text() == ip:
                        excl_item = QStandardItem("")
                        model.setItem(row, 10, excl_item)  # Colonne Excl (vide pour inclure)
                        logger.info(f"Hôte {ip} réinclus via API")
                        self.broadcast_update()
                        return jsonify({'success': True, 'message': f'Hôte {ip} réinclus'})
                
                return jsonify({'success': False, 'error': 'Hôte non trouvé'}), 404
            except Exception as e:
                logger.error(f"Erreur inclusion hôte: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/update_host_name', methods=['POST'])
        @WebAuth.login_required
        def update_host_name():
            try:
                data = request.get_json()
                ip = data.get('ip')
                new_name = data.get('name', '')
                
                # Import QStandardItem selon le mode
                if GUI_AVAILABLE:
                    from PySide6.QtGui import QStandardItem
                else:
                    # Version headless
                    class QStandardItem:
                        def __init__(self, text=""): 
                            self._text = str(text) if text else ""
                        def text(self): return self._text
                        def setText(self, text): self._text = str(text)
                
                model = self.main_window.treeIpModel
                for row in range(model.rowCount()):
                    item_ip = model.item(row, 1)  # Colonne IP
                    if item_ip and item_ip.text() == ip:
                        name_item = QStandardItem(new_name)
                        model.setItem(row, 2, name_item)  # Colonne Nom
                        logger.info(f"Nom de l'hôte {ip} modifié en '{new_name}' via API")
                        self.broadcast_update()
                        return jsonify({'success': True, 'message': f'Nom modifié pour {ip}'})
                
                return jsonify({'success': False, 'error': 'Hôte non trouvé'}), 404
            except Exception as e:
                logger.error(f"Erreur modification nom hôte: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/export_csv')
        def export_csv():
            try:
                import tempfile
                import os
                from src import fct
                
                # Créer un fichier temporaire
                temp_path = os.path.join(tempfile.gettempdir(), 'export_hosts.csv')
                
                # Générer le CSV
                fct.save_csv(self.main_window, self.main_window.treeIpModel, filepath=temp_path, return_path=True)
                logger.info("Export CSV via API")
                return send_file(temp_path, as_attachment=True, download_name='hosts.csv', mimetype='text/csv')
            except Exception as e:
                logger.error(f"Erreur export CSV: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/import_csv', methods=['POST'])
        @WebAuth.login_required
        def import_csv():
            try:
                if 'file' not in request.files:
                    return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'}), 400
                
                # Sauvegarder temporairement le fichier
                import tempfile
                import os
                temp_path = os.path.join(tempfile.gettempdir(), 'import.csv')
                file.save(temp_path)
                
                # Charger le CSV
                from src import fct
                fct.load_csv(self.main_window, self.main_window.treeIpModel, temp_path)
                
                # Nettoyer
                os.remove(temp_path)
                
                logger.info("Import CSV via API")
                self.broadcast_update()
                return jsonify({'success': True, 'message': 'Import réussi'})
            except Exception as e:
                logger.error(f"Erreur import CSV: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/export_xls')
        @WebAuth.login_required
        def export_xls():
            """Export XLS avec colonnes IP, Nom, Mac"""
            try:
                import tempfile
                import os
                from src import fctXls
                
                # Créer un fichier temporaire
                temp_path = os.path.join(tempfile.gettempdir(), 'export_hosts.xlsx')
                
                # Générer le XLS
                fctXls.export_xls_web(self.main_window.treeIpModel, temp_path)
                
                logger.info("Export XLS via API")
                return send_file(temp_path, as_attachment=True, download_name='hosts.xlsx', 
                               mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            except Exception as e:
                logger.error(f"Erreur export XLS: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/import_xls', methods=['POST'])
        @WebAuth.login_required
        def import_xls():
            """Import XLS avec colonnes IP, Nom, Mac"""
            try:
                if 'file' not in request.files:
                    return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400
                
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'}), 400
                
                # Vérifier l'extension
                if not file.filename.lower().endswith(('.xlsx', '.xls')):
                    return jsonify({'success': False, 'error': 'Format de fichier non supporté. Utilisez .xlsx'}), 400
                
                # Sauvegarder temporairement le fichier
                import tempfile
                import os
                temp_path = os.path.join(tempfile.gettempdir(), 'import.xlsx')
                file.save(temp_path)
                
                # Importer le XLS
                from src import fctXls
                result = fctXls.import_xls_web(self.main_window.treeIpModel, temp_path)
                
                # Nettoyer
                os.remove(temp_path)
                
                logger.info(f"Import XLS via API: {result['imported']} importé(s), {result['duplicates']} doublon(s)")
                self.broadcast_update()
                
                message = f"{result['imported']} hôte(s) importé(s)"
                if result['duplicates'] > 0:
                    message += f" ({result['duplicates']} doublon(s) ignoré(s))"
                
                return jsonify({'success': True, 'message': message, 'details': result})
            except Exception as e:
                logger.error(f"Erreur import XLS: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/save_settings', methods=['POST'])
        def save_settings():
            try:
                from src import db
                db.save_param_db()
                logger.info("Paramètres sauvegardés via API")
                return jsonify({'success': True, 'message': 'Paramètres sauvegardés'})
            except Exception as e:
                logger.error(f"Erreur sauvegarde paramètres: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/get_settings')
        def get_settings():
            try:
                from src import var, db, lic
                monitoring_running = False
                if hasattr(self.main_window, 'main_controller'):
                    # Le monitoring est en cours si ping_manager existe
                    monitoring_running = self.main_window.main_controller.ping_manager is not None
                
                # Charger les paramètres SMTP
                smtp_params = db.lire_param_mail()
                if not smtp_params or len(smtp_params) < 5:
                    smtp_params = ['', '', '', '', '', '']
                
                # Ordre dans la DB (sFenetre.py):
                # [0]=email, [1]=password, [2]=port, [3]=server, [4]=recipients, [5]=telegram_chatid
                
                # Charger les paramètres généraux
                general_params = db.lire_param_gene()
                if not general_params or len(general_params) < 3:
                    general_params = ['', '', 'nord']
                
                # Info licence
                license_active = lic.verify_license()
                license_days = 0
                if license_active:
                    try:
                        license_days = int(lic.jours_restants_licence().split()[0])
                    except:
                        license_days = 0
                
                return jsonify({
                    'success': True,
                    'delai': var.delais,
                    'nb_hs': var.nbrHs,
                    'alerts': {
                        'popup': var.popup,
                        'mail': var.mail,
                        'telegram': var.telegram,
                        'mail_recap': var.mailRecap,
                        'db_externe': var.dbExterne,
                        'temp_alert': var.tempAlert,
                        'temp_seuil': var.tempSeuil,
                        'temp_seuil_warning': var.tempSeuilWarning
                    },
                    'monitoring_running': monitoring_running,
                    'smtp': {
                        'server': smtp_params[3] if len(smtp_params) > 3 else '',
                        'port': smtp_params[2] if len(smtp_params) > 2 else '',
                        'email': smtp_params[0] if len(smtp_params) > 0 else '',
                        'recipients': smtp_params[4] if len(smtp_params) > 4 else ''
                    },
                    'telegram': {
                        'configured': bool(smtp_params[5] if len(smtp_params) > 5 else ''),
                        'chatid': smtp_params[5] if len(smtp_params) > 5 else ''
                    },
                    'general': {
                        'site': general_params[0],
                        'license': general_params[1] if len(general_params) > 1 else '',
                        'theme': general_params[2],
                        'advanced_title': general_params[3] if len(general_params) > 3 else 'Paramètres Avancés'
                    },
                    'license': {
                        'active': license_active,
                        'days_remaining': license_days
                    },
                    'version': var.version
                })
            except Exception as e:
                logger.error(f"Erreur récupération paramètres: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/update_general_setting', methods=['POST'])
        @WebAuth.login_required
        def update_general_setting():
            try:
                data = request.get_json()
                from src import db
                
                # Récupérer les paramètres actuels
                current = db.lire_param_gene()
                if not current:
                    current = ['', '', 'nord', 'Paramètres Avancés']
                
                # Mettre à jour seulement ce qui est passé
                site = data.get('site', current[0])
                license_key = data.get('license', current[1])
                theme = data.get('theme', current[2])
                advanced_title = data.get('advanced_title', current[3] if len(current) > 3 else 'Paramètres Avancés')
                
                db.save_param_gene(site, license_key, theme, advanced_title)
                
                logger.info(f"Paramètre général mis à jour: {data}")
                return jsonify({'success': True, 'message': 'Paramètre mis à jour'})
            except Exception as e:
                logger.error(f"Erreur mise à jour paramètre général: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/save_smtp', methods=['POST'])
        @WebAuth.login_required
        def save_smtp():
            try:
                data = request.get_json()
                from src import db
                
                # Ordre correct pour correspondre à l'interface Qt (sFenetre.py):
                # [0]=email, [1]=password, [2]=port, [3]=server, [4]=recipients, [5]=telegram_chatid
                
                # Charger les paramètres actuels pour garder le telegram_chatid
                current_params = db.lire_param_mail()
                telegram_chatid = current_params[5] if current_params and len(current_params) > 5 else ''
                
                variables = [
                    data.get('email', ''),      # 0: email expéditeur
                    data.get('password', ''),   # 1: password
                    data.get('port', ''),       # 2: port
                    data.get('server', ''),     # 3: serveur SMTP
                    data.get('recipients', ''), # 4: destinataires
                    telegram_chatid             # 5: telegram chat_id (conservé)
                ]
                
                db.save_param_mail(variables)
                logger.info("Paramètres SMTP sauvegardés via API")
                return jsonify({'success': True, 'message': 'Configuration SMTP sauvegardée'})
            except Exception as e:
                logger.error(f"Erreur sauvegarde SMTP: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/save_telegram', methods=['POST'])
        @WebAuth.login_required
        def save_telegram():
            """
            Sauvegarde la configuration Telegram de manière sécurisée.
            Le token est stocké dans secure_config (jamais exposé via l'API).
            """
            try:
                data = request.get_json()
                
                token = data.get('token', '')
                chatid = data.get('chatid', '')
                
                # Sauvegarder le token dans le nouveau système sécurisé
                try:
                    from src import secure_config
                    if token:
                        # Convertir les chat_ids en liste
                        chat_ids_list = [c.strip() for c in chatid.split(',') if c.strip()]
                        secure_config.save_telegram_config(
                            token=token,
                            chat_ids=chat_ids_list,
                            enabled=True
                        )
                        logger.info("Token Telegram sauvegardé dans secure_config")
                except Exception as e:
                    logger.error(f"Erreur sauvegarde secure_config Telegram: {e}")
                
                # Aussi sauvegarder les chat_ids dans l'ancien système pour compatibilité
                from src import db
                smtp_params = db.lire_param_mail()
                if not smtp_params or len(smtp_params) < 6:
                    smtp_params = ['', '', '', '', '', '']
                
                smtp_params_list = list(smtp_params)
                if len(smtp_params_list) > 5:
                    smtp_params_list[5] = chatid
                else:
                    while len(smtp_params_list) < 5:
                        smtp_params_list.append('')
                    smtp_params_list.append(chatid)
                
                db.save_param_mail(smtp_params_list)
                
                logger.info(f"Configuration Telegram sauvegardée: chat_ids={chatid}")
                return jsonify({'success': True, 'message': 'Configuration Telegram sauvegardée'})
            except Exception as e:
                logger.error(f"Erreur sauvegarde Telegram: {e}", exc_info=True)
                return jsonify({'success': False, 'error': 'Erreur de sauvegarde'}), 500
        
        @self.app.route('/api/test_telegram', methods=['POST'])
        @WebAuth.login_required
        def test_telegram():
            try:
                from src import thread_telegram
                
                # Envoyer un message de test
                test_message = "✅ Test - Ping ü\n\nSi vous recevez ce message, votre configuration Telegram fonctionne correctement !\n\n🤖 Bot Telegram configuré avec succès."
                
                thread_telegram.main(test_message)
                
                logger.info("Message de test Telegram envoyé")
                return jsonify({'success': True, 'message': 'Message de test envoyé sur Telegram'})
            except Exception as e:
                logger.error(f"Erreur test Telegram: {e}", exc_info=True)
                return jsonify({'success': False, 'error': f'Erreur: {str(e)}'}), 500
        
        @self.app.route('/api/test_smtp', methods=['POST'])
        @WebAuth.login_required
        def test_smtp():
            try:
                # Pas besoin de données JSON pour un simple test
                # Charger les paramètres SMTP depuis la config
                from src import db
                smtp_params = db.lire_param_mail()
                
                if not smtp_params or len(smtp_params) < 5:
                    return jsonify({'success': False, 'error': 'Configuration SMTP non trouvée'}), 400
                
                # Ordre dans la DB (sFenetre.py):
                # [0]=email, [1]=password, [2]=port, [3]=server, [4]=recipients, [5]=telegram_chatid
                smtp_email = smtp_params[0]
                smtp_password = smtp_params[1]
                smtp_port = smtp_params[2]
                smtp_server = smtp_params[3]
                recipients = smtp_params[4]
                
                if not smtp_server or not smtp_email or not recipients:
                    return jsonify({'success': False, 'error': 'Configuration SMTP incomplète'}), 400
                
                # Envoyer un email de test
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                message = MIMEMultipart()
                message['From'] = smtp_email
                message['To'] = recipients.split(',')[0].strip()  # Premier destinataire
                message['Subject'] = 'Test - Ping ü'
                
                body = f"""
Ceci est un email de test envoyé depuis Ping ü.

Si vous recevez ce message, votre configuration SMTP fonctionne correctement !

Serveur SMTP : {smtp_server}:{smtp_port}
Email expéditeur : {smtp_email}

---
Ping ü - Monitoring Réseau
"""
                message.attach(MIMEText(body, 'plain'))
                
                # Connexion et envoi (gérer port 465 SSL et port 587 STARTTLS)
                port_int = int(smtp_port)
                
                if port_int == 465:
                    # Port 465 : Connexion SSL directe
                    with smtplib.SMTP_SSL(smtp_server, port_int, timeout=10) as server:
                        server.login(smtp_email, smtp_password)
                        server.send_message(message)
                else:
                    # Port 587 ou autre : STARTTLS
                    with smtplib.SMTP(smtp_server, port_int, timeout=10) as server:
                        server.starttls()
                        server.login(smtp_email, smtp_password)
                        server.send_message(message)
                
                logger.info(f"Email de test SMTP envoyé à {recipients}")
                return jsonify({'success': True, 'message': f'Email de test envoyé à {recipients.split(",")[0].strip()}'})
                
            except smtplib.SMTPAuthenticationError:
                logger.error("Erreur d'authentification SMTP")
                return jsonify({'success': False, 'error': 'Erreur d\'authentification SMTP (vérifiez l\'email et le mot de passe)'}), 400
            except smtplib.SMTPServerDisconnected as e:
                logger.error(f"Connexion SMTP fermée: {e}")
                error_msg = 'Connexion fermée par le serveur. '
                if port_int == 587:
                    error_msg += 'Essayez le port 465 (SSL/TLS) ou vérifiez que le serveur supporte STARTTLS.'
                elif port_int == 465:
                    error_msg += 'Essayez le port 587 (STARTTLS) ou vérifiez la configuration SSL.'
                else:
                    error_msg += f'Port {port_int} inhabituel. Utilisez 587 (STARTTLS) ou 465 (SSL).'
                return jsonify({'success': False, 'error': error_msg}), 500
            except smtplib.SMTPException as e:
                logger.error(f"Erreur SMTP: {e}", exc_info=True)
                return jsonify({'success': False, 'error': f'Erreur SMTP: {str(e)}'}), 500
            except Exception as e:
                logger.error(f"Erreur test SMTP: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/save_general', methods=['POST'])
        @WebAuth.login_required
        def save_general():
            try:
                data = request.get_json()
                from src import db
                
                site = data.get('site', '')
                license_key = data.get('license', '')
                theme = data.get('theme', 'nord')
                
                db.save_param_gene(site, license_key, theme)
                logger.info("Paramètres généraux sauvegardés via API")
                return jsonify({'success': True, 'message': 'Paramètres généraux sauvegardés'})
            except Exception as e:
                logger.error(f"Erreur sauvegarde paramètres généraux: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/get_license_info')
        @WebAuth.login_required
        def get_license_info():
            try:
                from src import lic
                from src import lic_secure
                
                active = lic.verify_license()
                days = 0
                activation_code = ""
                
                try:
                    activation_code = lic_secure.generate_activation_code()
                except Exception as e:
                    logger.error(f"Erreur génération code activation: {e}")
                    activation_code = "Erreur"

                if active:
                    try:
                        days_str = lic.jours_restants_licence()
                        days = int(days_str.split()[0])
                    except:
                        days = 0
                
                return jsonify({
                    'success': True,
                    'active': active,
                    'days_remaining': days,
                    'activation_code': activation_code
                })
            except Exception as e:
                logger.error(f"Erreur info licence: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/get_user_info')
        @WebAuth.login_required
        def get_user_info():
            try:
                return jsonify({
                    'success': True,
                    'username': session.get('username', 'unknown')
                })
            except Exception as e:
                logger.error(f"Erreur info utilisateur: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/get_mail_recap_settings')
        @WebAuth.login_required
        def get_mail_recap_settings():
            try:
                from src import db
                settings = db.lire_param_mail_recap()
                
                if not settings or len(settings) < 8:
                    # Valeurs par défaut
                    from datetime import time
                    return jsonify({
                        'success': True,
                        'heure': '08:00',
                        'lundi': False,
                        'mardi': False,
                        'mercredi': False,
                        'jeudi': False,
                        'vendredi': False,
                        'samedi': False,
                        'dimanche': False
                    })
                
                # Convertir l'heure en chaîne
                heure_str = settings[0].strftime('%H:%M') if hasattr(settings[0], 'strftime') else str(settings[0])
                
                return jsonify({
                    'success': True,
                    'heure': heure_str,
                    'lundi': bool(settings[1]),
                    'mardi': bool(settings[2]),
                    'mercredi': bool(settings[3]),
                    'jeudi': bool(settings[4]),
                    'vendredi': bool(settings[5]),
                    'samedi': bool(settings[6]),
                    'dimanche': bool(settings[7])
                })
            except Exception as e:
                logger.error(f"Erreur récupération paramètres mail recap: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/save_mail_recap', methods=['POST'])
        @WebAuth.login_required
        def save_mail_recap():
            try:
                data = request.get_json()
                from src import db
                from datetime import time
                
                # Convertir l'heure
                heure_str = data.get('heure', '08:00')
                heure_parts = heure_str.split(':')
                heure = time(int(heure_parts[0]), int(heure_parts[1]))
                
                variables = [
                    heure,
                    data.get('lundi', False),
                    data.get('mardi', False),
                    data.get('mercredi', False),
                    data.get('jeudi', False),
                    data.get('vendredi', False),
                    data.get('samedi', False),
                    data.get('dimanche', False)
                ]
                
                db.save_param_mail_recap(variables)
                logger.info(f"Paramètres mail recap sauvegardés: {heure_str}, jours actifs")
                return jsonify({'success': True, 'message': 'Paramètres mail récapitulatif sauvegardés'})
            except Exception as e:
                logger.error(f"Erreur sauvegarde mail recap: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/send_test_recap', methods=['POST'])
        @WebAuth.login_required
        def send_test_recap():
            try:
                from src import email_sender
                
                # Récupérer les données des hôtes
                hosts_data = self._get_hosts_data()
                
                # Envoyer l'email recap de test
                result = email_sender.send_recap_email(hosts_data, test_mode=True)
                
                if result:
                    logger.info("Email récapitulatif de test envoyé")
                    return jsonify({'success': True, 'message': 'Email récapitulatif de test envoyé'})
                else:
                    return jsonify({'success': False, 'error': 'Erreur lors de l\'envoi de l\'email'}), 500
            except Exception as e:
                logger.error(f"Erreur test email recap: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # ==================== Gestion Multi-Sites ====================
        
        @self.app.route('/api/get_sites')
        @WebAuth.any_login_required
        def get_sites():
            """Récupère la liste des sites et leur état"""
            try:
                from src import var
                # On récupère aussi les sites présents dans le modèle pour ne rien oublier
                model = self.main_window.treeIpModel
                dynamic_sites = set()
                for row in range(model.rowCount()):
                    s = model.item(row, 8).text() if model.item(row, 8) else ''
                    if s:
                        dynamic_sites.add(s)
                
                # Fusionner avec la liste officielle
                all_sites = sorted(list(set(var.sites_list) | dynamic_sites))
                
                return jsonify({
                    'success': True,
                    'sites': all_sites,
                    'sites_actifs': var.sites_actifs,
                    'site_filter': var.site_filter
                })
            except Exception as e:
                logger.error(f"Erreur récupération sites: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/add_site', methods=['POST'])
        @WebAuth.login_required
        def add_site():
            """Ajoute un nouveau site"""
            try:
                data = request.get_json()
                site_name = data.get('name', '').strip()
                
                if not site_name:
                    return jsonify({'success': False, 'error': 'Nom de site requis'}), 400
                
                from src import var, db
                if site_name in var.sites_list:
                    return jsonify({'success': False, 'error': 'Ce site existe déjà'}), 400
                
                var.sites_list.append(site_name)
                db.save_sites()  # Sauvegarder
                logger.info(f"Site ajouté: {site_name}")
                return jsonify({'success': True, 'message': f'Site "{site_name}" ajouté', 'sites': var.sites_list})
            except Exception as e:
                logger.error(f"Erreur ajout site: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/delete_site', methods=['POST'])
        @WebAuth.login_required
        def delete_site():
            """Supprime un site"""
            try:
                data = request.get_json()
                site_name = data.get('name', '').strip()
                
                from src import var, db
                if site_name not in var.sites_list:
                    return jsonify({'success': False, 'error': 'Site non trouvé'}), 404
                
                var.sites_list.remove(site_name)
                
                # Retirer des listes actives aussi
                if site_name in var.sites_actifs:
                    var.sites_actifs.remove(site_name)
                if site_name in var.site_filter:
                    var.site_filter.remove(site_name)
                
                db.save_sites()  # Sauvegarder
                logger.info(f"Site supprimé: {site_name}")
                return jsonify({'success': True, 'message': f'Site "{site_name}" supprimé', 'sites': var.sites_list})
            except Exception as e:
                logger.error(f"Erreur suppression site: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/set_sites_actifs', methods=['POST'])
        @WebAuth.login_required
        def set_sites_actifs():
            """Définit les sites à surveiller (vide = tous)"""
            try:
                data = request.get_json()
                sites = data.get('sites', [])
                
                from src import var, db
                var.sites_actifs = sites
                db.save_sites()  # Sauvegarder
                
                logger.info(f"Sites actifs définis: {sites if sites else 'Tous'}")
                return jsonify({'success': True, 'message': 'Sites de surveillance mis à jour', 'sites_actifs': var.sites_actifs})
            except Exception as e:
                logger.error(f"Erreur définition sites actifs: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/set_site_filter', methods=['POST'])
        @WebAuth.login_required
        def set_site_filter():
            """Définit les sites à afficher (vide = tous)"""
            try:
                data = request.get_json()
                sites = data.get('sites', [])
                
                from src import var, db
                var.site_filter = sites
                db.save_sites()  # Sauvegarder
                
                logger.info(f"Filtre d'affichage défini: {sites if sites else 'Tous'}")
                self.broadcast_update()
                return jsonify({'success': True, 'message': 'Filtre mis à jour', 'site_filter': var.site_filter})
            except Exception as e:
                logger.error(f"Erreur définition filtre sites: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/set_host_site', methods=['POST'])
        @WebAuth.login_required
        def set_host_site():
            """Assigne un site à un hôte"""
            try:
                data = request.get_json()
                ip = data.get('ip')
                site_name = data.get('site', '')
                
                # Import QStandardItem selon le mode
                if GUI_AVAILABLE:
                    from PySide6.QtGui import QStandardItem
                else:
                    class QStandardItem:
                        def __init__(self, text=""): 
                            self._text = str(text) if text else ""
                        def text(self): return self._text
                        def setText(self, text): self._text = str(text)
                
                model = self.main_window.treeIpModel
                for row in range(model.rowCount()):
                    item_ip = model.item(row, 1)
                    if item_ip and item_ip.text() == ip:
                        site_item = model.item(row, 8)  # Colonne site
                        if not site_item:
                            site_item = QStandardItem(site_name)
                            model.setItem(row, 8, site_item)
                        else:
                            site_item.setText(site_name)
                        
                        logger.info(f"Site de l'hôte {ip} défini sur '{site_name}'")
                        self.broadcast_update()
                        return jsonify({'success': True, 'message': f'Site de {ip} mis à jour'})
                
                return jsonify({'success': False, 'error': 'Hôte non trouvé'}), 404
            except Exception as e:
                logger.error(f"Erreur assignation site hôte: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/set_multiple_hosts_site', methods=['POST'])
        @WebAuth.login_required
        def set_multiple_hosts_site():
            """Assigne un site à plusieurs hôtes"""
            try:
                data = request.get_json()
                ips = data.get('ips', [])
                site_name = data.get('site', '')
                
                if not ips:
                    return jsonify({'success': False, 'error': 'Aucune IP fournie'}), 400
                
                # Import QStandardItem selon le mode
                if GUI_AVAILABLE:
                    from PySide6.QtGui import QStandardItem
                else:
                    class QStandardItem:
                        def __init__(self, text=""): 
                            self._text = str(text) if text else ""
                        def text(self): return self._text
                        def setText(self, text): self._text = str(text)
                
                model = self.main_window.treeIpModel
                updated_count = 0
                
                for row in range(model.rowCount()):
                    item_ip = model.item(row, 1)
                    if item_ip and item_ip.text() in ips:
                        site_item = model.item(row, 8)  # Colonne site
                        if not site_item:
                            site_item = QStandardItem(site_name)
                            model.setItem(row, 8, site_item)
                        else:
                            site_item.setText(site_name)
                        updated_count += 1
                
                logger.info(f"{updated_count} hôte(s) assigné(s) au site '{site_name}'")
                self.broadcast_update()
                return jsonify({'success': True, 'message': f'{updated_count} hôte(s) mis à jour'})
            except Exception as e:
                logger.error(f"Erreur assignation multiple sites: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # ==================== Scanner Réseau ====================
        
        @self.app.route('/api/network_scan/start', methods=['POST'])
        @WebAuth.login_required
        def start_network_scan():
            """Démarre un scan réseau"""
            try:
                if not NETWORK_SCANNER_AVAILABLE or not self._network_scanner:
                    return jsonify({'success': False, 'error': 'Scanner réseau non disponible'}), 500
                
                data = request.get_json()
                scan_types = data.get('scan_types', ['hik', 'onvif', 'dahua', 'xiaomi', 'samsung', 'upnp'])
                timeout = data.get('timeout', 15)
                
                # Vérifier qu'aucun scan n'est en cours
                if self._scan_thread and self._scan_thread.is_alive():
                    return jsonify({'success': False, 'error': 'Un scan est déjà en cours'}), 400
                
                # Lancer le scan dans un thread séparé
                def run_scan():
                    try:
                        logger.info(f"Démarrage scan réseau: {scan_types}")
                        self.socketio.emit('scan_status', {'status': 'running', 'message': 'Scan démarré'})
                        self._network_scanner.scan_network(scan_types, timeout)
                        self.socketio.emit('scan_status', {'status': 'complete', 'message': 'Scan terminé'})
                        logger.info("Scan réseau terminé")
                    except Exception as e:
                        logger.error(f"Erreur durant le scan: {e}", exc_info=True)
                        self.socketio.emit('scan_status', {'status': 'error', 'message': str(e)})
                
                self._scan_thread = threading.Thread(target=run_scan)
                self._scan_thread.start()
                
                logger.info(f"Scan réseau démarré: types={scan_types}, timeout={timeout}s")
                return jsonify({'success': True, 'message': 'Scan démarré'})
            except Exception as e:
                logger.error(f"Erreur démarrage scan: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/network_scan/stop', methods=['POST'])
        @WebAuth.login_required
        def stop_network_scan():
            """Arrête le scan réseau en cours"""
            try:
                if not NETWORK_SCANNER_AVAILABLE or not self._network_scanner:
                    return jsonify({'success': False, 'error': 'Scanner réseau non disponible'}), 500
                
                self._network_scanner.stop_scan()
                logger.info("Arrêt du scan réseau demandé")
                return jsonify({'success': True, 'message': 'Scan arrêté'})
            except Exception as e:
                logger.error(f"Erreur arrêt scan: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/network_scan/status')
        @WebAuth.login_required
        def get_scan_status():
            """Récupère le statut du scan en cours"""
            try:
                if not NETWORK_SCANNER_AVAILABLE:
                    return jsonify({'success': False, 'error': 'Scanner non disponible'}), 500
                
                is_running = self._scan_thread and self._scan_thread.is_alive()
                devices_found = len(self._network_scanner.discovered_devices) if self._network_scanner else 0
                
                return jsonify({
                    'success': True,
                    'running': is_running,
                    'devices_found': devices_found
                })
            except Exception as e:
                logger.error(f"Erreur statut scan: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # ==================== Statistiques de Connexion ====================
        
        @self.app.route('/statistics')
        @WebAuth.any_login_required
        def statistics_page():
            """Page des statistiques de connexion (admin only)"""
            return render_template('statistics.html')
        
        @self.app.route('/api/stats/overview')
        @WebAuth.any_login_required
        def stats_overview():
            """Retourne les statistiques globales de connexion"""
            try:
                from src.connection_stats import stats_manager
                days = request.args.get('days', 30, type=int)
                stats = stats_manager.get_overview_stats(days)
                return jsonify({'success': True, 'data': stats})
            except ImportError:
                return jsonify({'success': False, 'error': 'Module de statistiques non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur stats overview: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stats/top')
        @WebAuth.any_login_required
        def stats_top_disconnectors():
            """Retourne les hôtes avec le plus de déconnexions"""
            try:
                from src.connection_stats import stats_manager
                limit = request.args.get('limit', 10, type=int)
                days = request.args.get('days', 30, type=int)
                data = stats_manager.get_top_disconnectors(limit, days)
                return jsonify({'success': True, 'data': data})
            except ImportError:
                return jsonify({'success': False, 'error': 'Module de statistiques non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur stats top: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stats/host/<path:ip>')
        @WebAuth.any_login_required
        def stats_host(ip):
            """Retourne les statistiques d'un hôte spécifique"""
            try:
                from src.connection_stats import stats_manager
                stats = stats_manager.get_host_stats(ip)
                events = stats_manager.get_host_events(ip, limit=50)
                return jsonify({'success': True, 'data': {'stats': stats, 'events': events}})
            except ImportError:
                return jsonify({'success': False, 'error': 'Module de statistiques non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur stats hôte {ip}: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stats/events')
        @WebAuth.login_required
        def stats_recent_events():
            """Retourne les événements récents"""
            try:
                from src.connection_stats import stats_manager
                limit = request.args.get('limit', 50, type=int)
                events = stats_manager.get_recent_events(limit)
                return jsonify({'success': True, 'data': events})
            except ImportError:
                return jsonify({'success': False, 'error': 'Module de statistiques non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur events récents: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stats/reset', methods=['POST'])
        @WebAuth.login_required
        def stats_reset():
            """Réinitialise toutes les statistiques"""
            try:
                from src.connection_stats import stats_manager
                deleted_count = stats_manager.reset_all_stats()
                return jsonify({
                    'success': True, 
                    'message': f'{deleted_count} événements supprimés',
                    'deleted_count': deleted_count
                })
            except ImportError:
                return jsonify({'success': False, 'error': 'Module de statistiques non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur réinitialisation stats: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stats/hosts')
        @WebAuth.login_required
        def stats_all_hosts():
            """Retourne la liste de TOUS les hôtes surveillés, avec indication si des stats existent"""
            try:
                from src.connection_stats import stats_manager
                
                # Récupérer les hôtes avec des événements
                tracked_hosts = stats_manager.get_all_tracked_hosts()
                tracked_ips = {h['ip'] for h in tracked_hosts}
                
                # Récupérer TOUS les hôtes du modèle
                model = self.main_window.treeIpModel
                all_hosts = []
                for row in range(model.rowCount()):
                    ip_item = model.item(row, 1)
                    name_item = model.item(row, 2)
                    if ip_item:
                        ip = ip_item.text()
                        hostname = name_item.text() if name_item else ip
                        # FIX: Récupérer le statut en temps réel depuis le ping manager
                        status = self._get_realtime_host_status(ip, model, row)
                        all_hosts.append({
                            'ip': ip,
                            'hostname': hostname,
                            'has_events': ip in tracked_ips,
                            'status': status  # Statut en temps réel
                        })
                
                return jsonify({'success': True, 'data': all_hosts})
            except ImportError:
                return jsonify({'success': False, 'error': 'Module de statistiques non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur liste hôtes stats: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500

        # ============= Monitoring Graphiques (Température & Débit) =============
        
        @self.app.route('/monitoring')
        @WebAuth.login_required
        def monitoring_page():
            """Page de monitoring avec graphiques de température et débit"""
            return render_template('monitoring.html')
        
        @self.app.route('/api/monitoring/hosts')
        @WebAuth.login_required
        def monitoring_hosts():
            """Liste des hôtes avec données de monitoring disponibles"""
            try:
                from src.monitoring_history import get_monitoring_manager
                manager = get_monitoring_manager()
                
                hosts_data = manager.get_hosts_with_data()
                
                # Enrichir avec les noms depuis le modèle
                model = self.main_window.treeIpModel
                result = []
                for ip, data in hosts_data.items():
                    hostname = ip
                    for row in range(model.rowCount()):
                        item_ip = model.item(row, 1)
                        if item_ip and item_ip.text() == ip:
                            name_item = model.item(row, 2)
                            hostname = name_item.text() if name_item else ip
                            break
                    
                    result.append({
                        'ip': ip,
                        'hostname': hostname,
                        'has_temperature': data.get('has_temperature', False),
                        'has_bandwidth': data.get('has_bandwidth', False)
                    })
                
                return jsonify({'success': True, 'data': result})
            except ImportError:
                return jsonify({'success': False, 'error': 'Module monitoring non disponible'}), 500
            except Exception as e:
                logger.error(f"Erreur liste hôtes monitoring: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/temperature/<ip>')
        @WebAuth.login_required
        def monitoring_temperature(ip):
            """Historique de température pour un hôte"""
            try:
                from src.monitoring_history import get_monitoring_manager
                manager = get_monitoring_manager()
                
                hours = request.args.get('hours', 24, type=int)
                data = manager.get_temperature_history(ip, hours)
                
                return jsonify({'success': True, 'data': data})
            except Exception as e:
                logger.error(f"Erreur historique température {ip}: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/bandwidth/<ip>')
        @WebAuth.login_required
        def monitoring_bandwidth(ip):
            """Historique de débit pour un hôte"""
            try:
                from src.monitoring_history import get_monitoring_manager
                manager = get_monitoring_manager()
                
                hours = request.args.get('hours', 24, type=int)
                data = manager.get_bandwidth_history(ip, hours)
                
                return jsonify({'success': True, 'data': data})
            except Exception as e:
                logger.error(f"Erreur historique débit {ip}: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # ============= Monitoring Switch Ports (Multi-interfaces) =============
        
        @self.app.route('/api/monitoring/switch/<ip>/interfaces')
        @WebAuth.login_required
        def monitoring_switch_interfaces(ip):
            """Liste toutes les interfaces d'un switch/équipement réseau"""
            try:
                if not SNMP_AVAILABLE or not snmp_helper:
                    return jsonify({'success': False, 'error': 'SNMP non disponible'}), 500
                
                # Paramètre pour filtrer les interfaces inactives
                filter_inactive = request.args.get('filter_inactive', 'true').lower() == 'true'
                
                # Appel asynchrone via run_until_complete
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    interfaces = loop.run_until_complete(
                        snmp_helper.get_all_interfaces(ip, filter_inactive)
                    )
                finally:
                    loop.close()
                
                if interfaces is None:
                    return jsonify({'success': False, 'error': 'Impossible de récupérer les interfaces (SNMP désactivé?)'}), 500
                
                return jsonify({'success': True, 'data': interfaces})
            except Exception as e:
                logger.error(f"Erreur récupération interfaces switch {ip}: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/switch/<ip>/ports_bandwidth')
        @WebAuth.login_required
        def monitoring_switch_ports_bandwidth(ip):
            """Récupère les débits de tous les ports d'un switch en temps réel"""
            try:
                if not SNMP_AVAILABLE or not snmp_helper:
                    return jsonify({'success': False, 'error': 'SNMP non disponible'}), 500
                
                # Paramètre optionnel pour filtrer les interfaces
                interfaces_param = request.args.get('interfaces', '')
                interface_indices = None
                if interfaces_param:
                    try:
                        interface_indices = [int(x.strip()) for x in interfaces_param.split(',') if x.strip()]
                    except ValueError:
                        return jsonify({'success': False, 'error': 'Format invalide pour le paramètre interfaces'}), 400
                
                # Appel asynchrone
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    bandwidth_data = loop.run_until_complete(
                        snmp_helper.get_all_ports_bandwidth(ip, interface_indices)
                    )
                finally:
                    loop.close()
                
                if bandwidth_data is None:
                    return jsonify({'success': False, 'error': 'Impossible de récupérer les débits (SNMP désactivé ou aucune interface active)'}), 500
                
                # Calculer les débits en Mbps si on a des données précédentes
                import src.var as var
                results = {}
                
                for iface_idx, current_data in bandwidth_data.items():
                    # Clé de cache unique pour chaque interface
                    cache_key = f"{ip}_{iface_idx}"
                    previous_data = var.traffic_cache.get(cache_key)
                    
                    if previous_data:
                        # Calculer le débit
                        bandwidth = snmp_helper.calculate_bandwidth_sync(current_data, previous_data)
                        if bandwidth:
                            results[str(iface_idx)] = {
                                'in_mbps': bandwidth['in_mbps'],
                                'out_mbps': bandwidth['out_mbps']
                            }
                        else:
                            results[str(iface_idx)] = {'in_mbps': 0.0, 'out_mbps': 0.0}
                    else:
                        # Première mesure, pas de débit calculable
                        results[str(iface_idx)] = {'in_mbps': 0.0, 'out_mbps': 0.0}
                    
                    # Sauvegarder pour le prochain calcul
                    var.traffic_cache[cache_key] = current_data
                
                return jsonify({'success': True, 'data': results})
            except Exception as e:
                logger.error(f"Erreur récupération débits ports switch {ip}: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/monitoring/switch/<ip>/ports_history')
        @WebAuth.login_required
        def monitoring_switch_ports_history(ip):
            """Historique des débits des ports d'un switch"""
            try:
                from src.monitoring_history import get_monitoring_manager
                manager = get_monitoring_manager()
                
                hours = request.args.get('hours', 24, type=int)
                
                # Paramètre pour filtrer les interfaces
                interfaces_param = request.args.get('interfaces', '')
                interface_indices = None
                if interfaces_param:
                    try:
                        interface_indices = [int(x.strip()) for x in interfaces_param.split(',') if x.strip()]
                    except ValueError:
                        return jsonify({'success': False, 'error': 'Format invalide pour le paramètre interfaces'}), 400
                
                # Récupérer l'historique pour chaque interface
                # Note: Cette fonctionnalité nécessite que monitoring_history soit étendu
                # Pour l'instant, on retourne une structure vide
                # TODO: Implémenter get_ports_bandwidth_history dans monitoring_history.py
                
                # Structure de retour attendue:
                # {
                #   '1': [{'timestamp': ..., 'in_mbps': ..., 'out_mbps': ...}, ...],
                #   '2': [{'timestamp': ..., 'in_mbps': ..., 'out_mbps': ...}, ...],
                # }
                
                result = {}
                if hasattr(manager, 'get_port_bandwidth_history'):
                    if interface_indices:
                        for idx in interface_indices:
                            data = manager.get_port_bandwidth_history(ip, idx, hours)
                            if data:
                                result[str(idx)] = data
                    else:
                        # Récupérer toutes les interfaces
                        result = manager.get_all_ports_bandwidth_history(ip, hours)
                else:
                    # Fallback: utiliser l'historique de l'interface principale
                    logger.warning("get_port_bandwidth_history non implémenté, utilisation de l'historique simple")
                    data = manager.get_bandwidth_history(ip, hours)
                    if data:
                        result['1'] = data  # Interface 1 par défaut
                
                return jsonify({'success': True, 'data': result})
            except Exception as e:
                logger.error(f"Erreur historique ports switch {ip}: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/synoptic')
        @WebAuth.any_login_required
        def synoptic():
            try:
                is_admin = session.get('role') == 'admin'
                username = session.get('username', '')
                return render_template('synoptic.html', is_admin=is_admin, username=username)
            except Exception as e:
                logger.error(f"Erreur rendu synoptic: {e}", exc_info=True)
                return jsonify({'error': 'Template introuvable', 'message': str(e)}), 500

        @self.app.route('/api/synoptic/upload', methods=['POST'])
        @WebAuth.login_required
        def upload_synoptic_map():
            try:
                if 'map_image' not in request.files:
                    return jsonify({'success': False, 'error': 'Aucun fichier fourni'}), 400
                
                file = request.files['map_image']
                if file.filename == '':
                    return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'}), 400
                
                # Vérifier l'extension (PNG uniquement comme demandé)
                if not file.filename.lower().endswith('.png'):
                    return jsonify({'success': False, 'error': 'Format de fichier non supporté. Utilisez .png'}), 400

                # Sauvegarder dans bd/synoptic.png
                # Utiliser chemin relatif 'bd' si existant, sinon créer
                bd_dir = "bd"
                if not os.path.exists(bd_dir):
                    os.makedirs(bd_dir, exist_ok=True)
                
                dest_path = os.path.join(bd_dir, "synoptic.png")
                file.save(dest_path)
                
                logger.info(f"Image synoptique uploadée: {dest_path}")
                return jsonify({'success': True, 'message': 'Image uploadée avec succès'})
            except Exception as e:
                logger.error(f"Erreur upload synoptic: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/synoptic/config', methods=['GET', 'POST'])
        @WebAuth.any_login_required
        def synoptic_config():
            bd_dir = "bd"
            config_path = os.path.join(bd_dir, "synoptic.json")
            
            try:
                if request.method == 'POST':
                    # Seul admin peut sauvegarder
                    if session.get('role') != 'admin':
                        return jsonify({'success': False, 'error': 'Non autorisé'}), 403
                        
                    data = request.get_json()
                    
                    if not os.path.exists(bd_dir):
                        os.makedirs(bd_dir, exist_ok=True)
                        
                    with open(config_path, 'w') as f:
                        json.dump(data, f, indent=4)
                        
                    logger.info("Configuration synoptique sauvegardée")
                    return jsonify({'success': True, 'message': 'Configuration sauvegardée'})
                
                else: # GET
                    if os.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            data = json.load(f)
                        return jsonify({'success': True, 'config': data})
                    else:
                        return jsonify({'success': True, 'config': {}})
                        
            except Exception as e:
                logger.error(f"Erreur config synoptic: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/synoptic/image')
        @WebAuth.any_login_required
        def get_synoptic_image():
            try:
                bd_dir = os.path.abspath("bd")
                image_path = os.path.join(bd_dir, "synoptic.png")
                
                if os.path.exists(image_path):
                    return send_file(image_path, mimetype='image/png')
                else:
                    return jsonify({'error': 'Image non trouvée'}), 404
            except Exception as e:
                logger.error(f"Erreur image synoptic: {e}", exc_info=True)
                return jsonify({'error': str(e)}), 500

    def _on_device_discovered(self, device):
        """Callback appelé quand un périphérique est découvert"""
        try:
            # Envoyer via WebSocket
            self.socketio.emit('scan_device_found', device.to_dict())
            logger.info(f"Périphérique découvert: {device.ip} ({device.device_type.value})")
        except Exception as e:
            logger.error(f"Erreur callback device discovered: {e}", exc_info=True)
    
    def _setup_socketio(self):
        """Configuration des événements Socket.IO"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client web connecté")
            try:
                hosts = self._get_hosts_data()
                emit('hosts_update', hosts)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi initial: {e}", exc_info=True)
                emit('hosts_update', [])
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("Client web déconnecté")
        
        @self.socketio.on('request_update')
        def handle_request_update():
            try:
                hosts = self._get_hosts_data()
                emit('hosts_update', hosts)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi: {e}", exc_info=True)
                emit('hosts_update', [])
        
        @self.socketio.on_error_default
        def default_error_handler(e):
            """Gestionnaire d'erreur global pour Socket.IO"""
            # Ignorer les erreurs bénignes de WebSocket
            error_str = str(e)
            if 'write() before start_response' not in error_str:
                logger.debug(f"Erreur Socket.IO (ignorée): {error_str}")
    
    def _get_hosts_data(self, apply_filter=True):
        """Extrait les données du treeview avec filtrage optionnel par site"""
        hosts = []
        try:
            from src import var
            model = self.main_window.treeIpModel
            row_count = model.rowCount()
            
            if row_count == 0:
                return hosts
            
            for row in range(row_count):
                try:
                    # S'assurer que tous les items existent
                    item_ip = model.item(row, 1)
                    if not item_ip:
                        continue
                    
                    ip = item_ip.text() if item_ip else ''
                    if not ip:
                        continue
                    
                    # Récupérer le site de l'hôte (colonne site = colonne 8)
                    site = model.item(row, 8).text() if model.item(row, 8) else ''
                    
                    # Filtrage par site si activé
                    if apply_filter and var.site_filter:
                        # Si un filtre est défini et que l'hôte n'est pas dans les sites filtrés
                        if site not in var.site_filter:
                            continue
                    
                    latence_text = model.item(row, 5).text() if model.item(row, 5) else 'N/A'
                    
                    # Calculer la couleur de latence
                    latency_color = self._get_latency_color(latence_text)
                    
                    host_data = {
                        'id': model.item(row, 0).text() if model.item(row, 0) else str(row),
                        'ip': ip,
                        'nom': model.item(row, 2).text() if model.item(row, 2) else ip,
                        'mac': model.item(row, 3).text() if model.item(row, 3) else '',
                        'port': model.item(row, 4).text() if model.item(row, 4) else '',
                        'latence': latence_text,
                        'latency_color': latency_color,
                        'temp': model.item(row, 6).text() if model.item(row, 6) else '-',
                        'suivi': model.item(row, 7).text() if model.item(row, 7) else '',
                        'site': site,  # Renommé de 'comm' à 'site'
                        'commentaire': model.item(row, 9).text() if model.item(row, 9) else '',
                        'excl': model.item(row, 10).text() if model.item(row, 10) else '',
                        'status': self._get_row_status(model, row)
                    }
                    
                    # Récupération des débits depuis le cache (non bloquant)
                    bandwidth = self._get_cached_bandwidth(ip)
                    host_data['debit_in'] = bandwidth['in']
                    host_data['debit_out'] = bandwidth['out']
                    
                    # Vérifier que toutes les valeurs sont sérialisables
                    for key, value in host_data.items():
                        if value is None:
                            host_data[key] = ''
                        elif not isinstance(value, (str, int, float, bool)):
                            host_data[key] = str(value)
                    
                    hosts.append(host_data)
                    
                except Exception as row_error:
                    logger.error(f"Erreur lors de l'extraction de la ligne {row}: {row_error}")
                    continue
            
        except Exception as e:
            logger.error(f"Erreur extraction données hôtes: {e}", exc_info=True)
        
        return hosts
    
    def _get_cached_bandwidth(self, ip):
        """
        Récupère le débit depuis le cache (non bloquant).
        Les débits sont calculés par le PingManager pendant le monitoring.
        """
        try:
            # Vérifier si le PingManager existe et a un cache
            if hasattr(self.main_window, 'main_controller') and \
               self.main_window.main_controller and \
               hasattr(self.main_window.main_controller, 'ping_manager') and \
               self.main_window.main_controller.ping_manager:
                
                ping_manager = self.main_window.main_controller.ping_manager
                
                # Récupérer le cache de trafic du PingManager (persiste entre les cycles)
                if hasattr(ping_manager, 'traffic_cache'):
                    traffic_cache = ping_manager.traffic_cache
                    
                    # Vérifier si on a des données pour cette IP
                    if ip in traffic_cache:
                        # Calculer le débit depuis le cache
                        current_data = traffic_cache.get(ip)
                        previous_data = self.traffic_cache.get(ip)
                        
                        if current_data and previous_data and SNMP_AVAILABLE:
                            bandwidth = snmp_helper.calculate_bandwidth_sync(current_data, previous_data)
                            if bandwidth:
                                # Sauvegarder dans notre cache avec formatage automatique des unités
                                self.traffic_cache[ip] = current_data
                                self._bandwidth_cache[ip] = {
                                    'in': format_bandwidth(bandwidth['in_mbps']),
                                    'out': format_bandwidth(bandwidth['out_mbps'])
                                }
                                return self._bandwidth_cache[ip]
                        
                        # Sauvegarder les données actuelles pour le prochain calcul
                        if current_data:
                            self.traffic_cache[ip] = current_data
            
            # Retourner le dernier débit connu ou '-'
            if ip in self._bandwidth_cache:
                return self._bandwidth_cache[ip]
            
            return {'in': '-', 'out': '-'}
            
        except Exception as e:
            logger.debug(f"Erreur récupération débit depuis cache pour {ip}: {e}")
            return {'in': '-', 'out': '-'}
    
    def _get_bandwidth_for_host(self, ip):
        """
        Méthode obsolète - conservée pour compatibilité.
        Utiliser _get_cached_bandwidth() à la place.
        """
        return self._get_cached_bandwidth(ip)
    
    def _clean_alert_lists_for_new_threshold(self, new_threshold):
        """
        Nettoie les listes d'alertes pour s'adapter au nouveau seuil.
        Si un compteur dépasse le nouveau seuil, il est ramené au nouveau seuil - 1.
        Les états spéciaux (10 et 20) sont préservés.
        Cela évite les alertes immédiates lors du changement de configuration.
        """
        try:
            from src import var
            
            # Fonction pour nettoyer une liste
            def clean_list(liste, list_name):
                cleaned_count = 0
                for ip, count in list(liste.items()):
                    count_int = int(count)
                    # Les états spéciaux (10 = alerte envoyée, 20 = retour OK) ne doivent jamais être modifiés
                    if count_int >= 10:
                        continue
                    # Si le compteur dépasse ou égale le nouveau seuil, on le limite
                    if count_int >= new_threshold:
                        liste[ip] = max(1, new_threshold - 1)
                        cleaned_count += 1
                return cleaned_count
            
            hs_cleaned = clean_list(var.liste_hs, "liste_hs")
            mail_cleaned = clean_list(var.liste_mail, "liste_mail")
            telegram_cleaned = clean_list(var.liste_telegram, "liste_telegram")
            
            total_cleaned = hs_cleaned + mail_cleaned + telegram_cleaned
            if total_cleaned > 0:
                logger.info(f"Nettoyage des listes d'alertes pour nouveau seuil {new_threshold}: "
                           f"{hs_cleaned} HS, {mail_cleaned} mail, {telegram_cleaned} telegram")
            
        except Exception as e:
            logger.error(f"Erreur nettoyage listes alertes: {e}", exc_info=True)
    
    def _get_row_status(self, model, row):
        """Détermine le statut (online/offline) selon la colonne Latence"""
        try:
            # Colonne 5 = "Latence" qui contient "HS" pour les hôtes hors service
            latence_item = model.item(row, 5)
            if latence_item:
                latence_text = latence_item.text().strip().upper()
                # Si la colonne contient "HS", l'hôte est hors ligne
                if latence_text == "HS":
                    return 'offline'
                else:
                    return 'online'
        except:
            pass
        # Par défaut, considérer comme en ligne
        return 'online'
    
    def _get_realtime_host_status(self, ip, model, row):
        """
        Détermine le statut en temps réel d'un hôte.
        Vérifie d'abord le ping manager pour l'état actuel,
        puis se rabat sur la colonne latence du modèle.
        """
        try:
            # Vérifier si le monitoring est actif et récupérer l'état réel
            if hasattr(self.main_window, 'main_controller') and \
               self.main_window.main_controller and \
               hasattr(self.main_window.main_controller, 'ping_manager') and \
               self.main_window.main_controller.ping_manager:
                
                ping_manager = self.main_window.main_controller.ping_manager
                
                # Vérifier si l'IP est dans les hôtes suivis
                if hasattr(ping_manager, 'host_states') and ip in ping_manager.host_states:
                    # Récupérer l'état réel depuis le ping manager
                    host_state = ping_manager.host_states[ip]
                    # Si le dernier ping a réussi, l'hôte est online
                    if host_state.get('is_alive', False):
                        return 'online'
                    else:
                        return 'offline'
        except Exception as e:
            logger.debug(f"Erreur récupération statut temps réel pour {ip}: {e}")
        
        # Fallback: utiliser la méthode existante basée sur la colonne latence
        return self._get_row_status(model, row)
    
    def _get_latency_color(self, latence_text):
        """
        Retourne la couleur correspondant à la latence.
        
        Règles:
        - < 100ms : vert clair (#baf595)
        - 100ms à 200ms : jaune clair (#fffd6a)
        - > 200ms (mais < 500ms / HS) : orange clair (#ffb845)
        - HS (offline) : rouge (#f97e7e)
        """
        try:
            if not latence_text or latence_text.strip().upper() == 'HS' or latence_text == 'N/A':
                return '#f97e7e'  # Rouge - HS
            
            # Extraire la valeur numérique de la latence (ex: "45.2 ms" -> 45.2)
            import re
            match = re.search(r'([\d.]+)', latence_text)
            if match:
                latency_ms = float(match.group(1))
                
                if latency_ms >= 500:
                    return '#f97e7e'  # Rouge - HS
                elif latency_ms > 200:
                    return '#ffb845'  # Orange clair - latence élevée
                elif latency_ms >= 100:
                    return '#fffd6a'  # Jaune clair - latence moyenne
                else:
                    return '#baf595'  # Vert clair - bonne latence
            
            return '#baf595'  # Par défaut vert
        except Exception:
            return '#baf595'  # Par défaut vert en cas d'erreur
    
    def _get_hosts_count(self):
        """Compte le nombre d'hôtes"""
        try:
            return self.main_window.treeIpModel.rowCount()
        except:
            return 0
    
    def start(self):
        """Démarre le serveur web"""
        if not FLASK_AVAILABLE:
            logger.error("Flask/SocketIO non installés. Le serveur web ne peut pas démarrer.")
            return False

        if self.running:
            logger.warning("Serveur web déjà en cours d'exécution")
            return False
        
        try:
            if not self._is_port_available(self.port):
                logger.error(f"Le port {self.port} est déjà utilisé")
                return False
            
            self.running = True
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            # Vérifier immédiatement le nombre d'hôtes
            try:
                row_count = self.main_window.treeIpModel.rowCount()
                logger.info(f"Serveur web démarré avec {row_count} hôtes dans le modèle")
            except Exception as e:
                logger.warning(f"Impossible de vérifier le nombre d'hôtes: {e}")
            
            local_ip = self._get_local_ip()
            logger.info(f"Serveur web accessible sur http://{local_ip}:{self.port}")
            logger.info(f"Accessible localement sur http://localhost:{self.port}")
            
            return True
        except Exception as e:
            logger.error(f"Erreur démarrage serveur web: {e}", exc_info=True)
            self.running = False
            return False
    
    def _run_server(self):
        """Exécute le serveur Flask-SocketIO"""
        try:
            # Désactiver les logs Werkzeug verbeux
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)  # Ne montrer que les vraies erreurs
            
            # Supprimer les handlers existants pour éviter la duplication et filtrer stderr
            for h in log.handlers[:]:
                log.removeHandler(h)
                
            # Filtre personnalisé pour ignorer l'erreur spécifique "write() before start_response"
            # qui est un bug connu de Werkzeug/SocketIO en mode threading mais inoffensif
            class IgnoreWriteErrorFilter(logging.Filter):
                def filter(self, record):
                    return "write() before start_response" not in record.getMessage()
            
            log.addFilter(IgnoreWriteErrorFilter())
            
            self.socketio.run(self.app, 
                            host='0.0.0.0',
                            port=self.port, 
                            debug=False, 
                            allow_unsafe_werkzeug=True,
                            use_reloader=False)
        except Exception as e:
            logger.error(f"Erreur exécution serveur: {e}", exc_info=True)
        finally:
            self.running = False
    
    def stop(self):
        """Arrête le serveur web"""
        if not self.running:
            return
        
        try:
            self.running = False
            logger.info("Arrêt du serveur web demandé")
            if hasattr(self, 'socketio') and self.socketio:
                # Tentative d'arrêt propre du serveur SocketIO
                try:
                    self.socketio.stop()
                    
                    # Hack pour débloquer le serveur s'il est coincé en attente de requête
                    # Envoie une connexion dummy pour forcer le réveil du thread
                    try:
                        import socket
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(0.1)
                            s.connect(('127.0.0.1', self.port))
                    except:
                        pass
                except:
                    pass
            
            # Attendre la fin du thread
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=1.0)
                if self.server_thread.is_alive():
                    logger.warning("Le thread du serveur web ne s'est pas arrêté proprement")
                
        except Exception as e:
            logger.error(f"Erreur arrêt serveur web: {e}", exc_info=True)
    
    def broadcast_update(self):
        """Diffuse une mise à jour à tous les clients connectés"""
        if self.socketio and self.running:
            try:
                # Pour le broadcast temps réel, on envoie tous les hôtes
                # Le filtrage est géré côté client (index.html)
                hosts = self._get_hosts_data(apply_filter=False)
                self.socketio.emit('hosts_update', hosts, namespace='/')
                
                # Envoyer aussi le statut du scan
                monitoring_running = False
                if hasattr(self.main_window, 'main_controller'):
                    monitoring_running = self.main_window.main_controller.ping_manager is not None
                self.socketio.emit('monitoring_status', {'running': monitoring_running}, namespace='/')
            except Exception as e:
                logger.error(f"Erreur diffusion mise à jour: {e}", exc_info=True)
    
    def emit_scan_complete(self, hosts_count):
        """Émet un événement quand le scan est terminé"""
        if not self.running:
            return
        
        try:
            self.socketio.emit('scan_complete', {'count': hosts_count}, namespace='/')
            logger.info(f"Scan terminé: {hosts_count} hôte(s) scanné(s)")
        except Exception as e:
            logger.error(f"Erreur émission scan complete: {e}", exc_info=True)
    
    def _is_port_available(self, port):
        """Vérifie si un port est disponible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Ajout de SO_REUSEADDR pour cohérence avec fct.find_available_port
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('', port))
                return True
        except OSError:
            return False
    
    def _get_local_ip(self):
        """Obtient l'adresse IP locale"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_access_urls(self):
        """Retourne les URLs d'accès au serveur"""
        local_ip = self._get_local_ip()
        return {
            'local': f'http://localhost:{self.port}',
            'network': f'http://{local_ip}:{self.port}'
        }

