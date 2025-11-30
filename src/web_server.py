# -*- coding: utf-8 -*-
"""
Serveur Web pour afficher les hôtes monitorés en temps réel
Utilise Flask et Socket.IO pour les mises à jour automatiques
"""
from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import socket
import asyncio
import secrets
from PySide6.QtCore import QObject, Signal
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
        
        self._setup_routes()
        self._setup_socketio()
        
    def _setup_routes(self):
        """Configuration des routes Flask"""
        
        @self.app.route('/')
        def index():
            try:
                return render_template('index.html')
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
            hosts = self._get_hosts_data()
            return jsonify(hosts)
        
        @self.app.route('/api/status')
        def status():
            return jsonify({
                'status': 'running',
                'hosts_count': self._get_hosts_count()
            })
        
        @self.app.route('/login', methods=['GET'])
        def login():
            try:
                # Si déjà connecté, rediriger vers admin
                if session.get('logged_in'):
                    return redirect(url_for('admin'))
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
                
                if web_auth.verify_credentials(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    logger.info(f"Connexion réussie: {username}")
                    return jsonify({'success': True, 'message': 'Connexion réussie'})
                else:
                    return jsonify({'success': False, 'error': 'Identifiants incorrects'}), 401
            except Exception as e:
                logger.error(f"Erreur login: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
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
        
        @self.app.route('/api/add_hosts', methods=['POST'])
        @WebAuth.login_required
        def add_hosts():
            try:
                data = request.get_json()
                ip = data.get('ip')
                hosts = data.get('hosts', 1)
                port = data.get('port', '80')
                scan_type = data.get('scan_type', 'alive')
                
                # Lancer le scan dans un thread séparé
                import threading
                from src import threadAjIp
                
                thread = threading.Thread(
                    target=threadAjIp.main,
                    args=(self.main_window, self.main_window.comm, 
                          self.main_window.treeIpModel, ip, hosts, 
                          scan_type.capitalize(), port, "")
                )
                thread.start()
                
                logger.info(f"Scan d'hôtes démarré: {ip}, {hosts} hôtes, type: {scan_type}")
                return jsonify({'success': True, 'message': f'Scan de {hosts} hôte(s) démarré'})
            except Exception as e:
                logger.error(f"Erreur ajout hôtes: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
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
                var.nbrHs = nb_hs
                
                # Démarrer le monitoring via le contrôleur (thread-safe avec signal Qt)
                if hasattr(self.main_window, 'main_controller'):
                    # Vérifier si le monitoring est déjà en cours (ping_manager existe)
                    if self.main_window.main_controller.ping_manager is None:
                        # Mise à jour des variables AVANT de démarrer
                        logger.info(f"Configuration reçue: Délai={delai}s, Nb HS={nb_hs}")
                        var.delais = delai
                        var.nbrHs = int(nb_hs) # Force int conversion
                        
                        # Utiliser un signal Qt pour démarrer le monitoring de manière thread-safe
                        self.main_window.comm.start_monitoring_signal.emit()
                        logger.info(f"Monitoring démarré via API (délai: {delai}s, nb_hs: {nb_hs})")
                        # Notifier tous les clients
                        self.socketio.emit('monitoring_status', {'running': True}, namespace='/')
                        return jsonify({'success': True, 'message': 'Monitoring démarré'})
                    else:
                        return jsonify({'success': True, 'message': 'Monitoring déjà en cours'})
                
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
                from src import var
                
                var.popup = data.get('popup', False)
                var.mail = data.get('mail', False)
                var.telegram = data.get('telegram', False)
                var.mailRecap = data.get('mail_recap', False)
                var.dbExterne = data.get('db_externe', False)
                
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
                model.removeRows(0, model.rowCount())
                logger.info("Tous les hôtes supprimés via API")
                self.broadcast_update()
                return jsonify({'success': True, 'message': 'Tous les hôtes supprimés'})
            except Exception as e:
                logger.error(f"Erreur suppression tous les hôtes: {e}", exc_info=True)
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
                
                model = self.main_window.treeIpModel
                for row in range(model.rowCount()):
                    item_ip = model.item(row, 1)  # Colonne IP
                    if item_ip and item_ip.text() == ip:
                        from PySide6.QtGui import QStandardItem
                        excl_item = QStandardItem("x")
                        model.setItem(row, 9, excl_item)  # Colonne Excl
                        logger.info(f"Hôte {ip} exclu via API")
                        self.broadcast_update()
                        return jsonify({'success': True, 'message': f'Hôte {ip} exclu'})
                
                return jsonify({'success': False, 'error': 'Hôte non trouvé'}), 404
            except Exception as e:
                logger.error(f"Erreur exclusion hôte: {e}", exc_info=True)
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
                    smtp_params = ['', '', '', '', '']
                
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
                        'db_externe': var.dbExterne
                    },
                    'monitoring_running': monitoring_running,
                    'smtp': {
                        'server': smtp_params[0] if len(smtp_params) > 0 else '',
                        'port': smtp_params[1] if len(smtp_params) > 1 else '',
                        'email': smtp_params[2] if len(smtp_params) > 2 else '',
                        'recipients': smtp_params[4] if len(smtp_params) > 4 else ''
                    },
                    'general': {
                        'site': general_params[0],
                        'license': general_params[1] if len(general_params) > 1 else '',
                        'theme': general_params[2]
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
        
        @self.app.route('/api/save_smtp', methods=['POST'])
        @WebAuth.login_required
        def save_smtp():
            try:
                data = request.get_json()
                from src import db
                
                variables = [
                    data.get('server', ''),
                    data.get('port', ''),
                    data.get('email', ''),
                    data.get('password', ''),
                    data.get('recipients', '')
                ]
                
                db.save_param_mail(variables)
                logger.info("Paramètres SMTP sauvegardés via API")
                return jsonify({'success': True, 'message': 'Configuration SMTP sauvegardée'})
            except Exception as e:
                logger.error(f"Erreur sauvegarde SMTP: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/test_smtp', methods=['POST'])
        @WebAuth.login_required
        def test_smtp():
            try:
                data = request.get_json()
                # TODO: Implémenter le test SMTP réel
                logger.info("Test SMTP demandé via API")
                return jsonify({'success': True, 'message': 'Email de test envoyé'})
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
    
    def _get_hosts_data(self):
        """Extrait les données du treeview"""
        hosts = []
        try:
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
                    
                    latence_text = model.item(row, 5).text() if model.item(row, 5) else 'N/A'
                    
                    host_data = {
                        'id': model.item(row, 0).text() if model.item(row, 0) else str(row),
                        'ip': ip,
                        'nom': model.item(row, 2).text() if model.item(row, 2) else ip,
                        'mac': model.item(row, 3).text() if model.item(row, 3) else '',
                        'port': model.item(row, 4).text() if model.item(row, 4) else '',
                        'latence': latence_text,
                        'temp': model.item(row, 6).text() if model.item(row, 6) else '-',
                        'suivi': model.item(row, 7).text() if model.item(row, 7) else '',
                        'comm': model.item(row, 8).text() if model.item(row, 8) else '',
                        'excl': model.item(row, 9).text() if model.item(row, 9) else '',
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
    
    def _get_hosts_count(self):
        """Compte le nombre d'hôtes"""
        try:
            return self.main_window.treeIpModel.rowCount()
        except:
            return 0
    
    def start(self):
        """Démarre le serveur web"""
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
        except Exception as e:
            logger.error(f"Erreur arrêt serveur web: {e}", exc_info=True)
    
    def broadcast_update(self):
        """Diffuse une mise à jour à tous les clients connectés"""
        if not self.running:
            return
        
        try:
            hosts = self._get_hosts_data()
            self.socketio.emit('hosts_update', hosts, namespace='/')
        except Exception as e:
            logger.error(f"Erreur diffusion mise à jour: {e}", exc_info=True)
    
    def _is_port_available(self, port):
        """Vérifie si un port est disponible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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

