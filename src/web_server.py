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
    from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS
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
                        "Id", "IP", "Nom", "Mac", "Port", "Latence", "Temp", "Suivi", "Comm", "Excl"
                    ])
                else:
                    for i in range(count_before - 1, -1, -1):
                        model.removeRow(i)
                
                # Vider aussi les listes d'alertes
                from src import var
                var.liste_hs.clear()
                var.liste_mail.clear()
                var.liste_telegram.clear()
                
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
                        model.setItem(row, 9, excl_item)  # Colonne Excl
                        
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
                        model.setItem(row, 9, excl_item)  # Colonne Excl (vide pour inclure)
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
                        'temp_seuil': var.tempSeuil
                    },
                    'monitoring_running': monitoring_running,
                    'smtp': {
                        'server': smtp_params[3] if len(smtp_params) > 3 else '',
                        'port': smtp_params[2] if len(smtp_params) > 2 else '',
                        'email': smtp_params[0] if len(smtp_params) > 0 else '',
                        'recipients': smtp_params[4] if len(smtp_params) > 4 else ''
                    },
                    'telegram': {
                        'token': '5584289469:AAHYRhZhDCXKE5l1v1UbLs-MUKGPoimMYAQ',
                        'chatid': smtp_params[5] if len(smtp_params) > 5 else ''
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
            try:
                data = request.get_json()
                from src import db
                
                token = data.get('token', '')
                chatid = data.get('chatid', '')
                
                # Charger les paramètres mail actuels
                smtp_params = db.lire_param_mail()
                if not smtp_params or len(smtp_params) < 6:
                    smtp_params = ['', '', '', '', '', '']
                
                # Mettre à jour le chat_id (index 5)
                smtp_params_list = list(smtp_params)
                if len(smtp_params_list) > 5:
                    smtp_params_list[5] = chatid
                else:
                    # Étendre la liste si nécessaire
                    while len(smtp_params_list) < 5:
                        smtp_params_list.append('')
                    smtp_params_list.append(chatid)
                
                # Sauvegarder
                db.save_param_mail(smtp_params_list)
                
                logger.info(f"Configuration Telegram sauvegardée: chat_id={chatid}")
                return jsonify({'success': True, 'message': 'Configuration Telegram sauvegardée'})
            except Exception as e:
                logger.error(f"Erreur sauvegarde Telegram: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
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

