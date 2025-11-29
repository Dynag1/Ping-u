# -*- coding: utf-8 -*-
"""
Serveur Web pour afficher les hôtes monitorés en temps réel
Utilise Flask et Socket.IO pour les mises à jour automatiques
"""
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import socket
import asyncio
from PySide6.QtCore import QObject, Signal
from src.utils.logger import get_logger
from src.utils.colors import format_bandwidth

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
    
    def __init__(self, main_window, port=5000):
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
                return f"Erreur: {e}", 500
        
        @self.app.route('/test')
        def test_page():
            try:
                return render_template('test_simple.html')
            except Exception as e:
                logger.error(f"Erreur lors du rendu du template de test: {e}", exc_info=True)
                return f"Erreur: {e}", 500
        
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
            self.socketio.emit('hosts_update', hosts, broadcast=True, namespace='/')
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

