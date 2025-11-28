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
            # Mode PyInstaller
            base_path = sys._MEIPASS
        else:
            # Mode développement
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        template_path = os.path.join(base_path, 'web', 'templates')
        static_path = os.path.join(base_path, 'web', 'static')
        
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
                                engineio_logger=False)
        self.server_thread = None
        self.running = False
        
        # Cache pour les débits SNMP (uniquement pour la page web)
        self.traffic_cache = {}
        
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
                    
                    # Désactiver temporairement SNMP pour éviter les problèmes de sérialisation
                    # TODO: Réactiver après avoir résolu le problème de WebSocket
                    host_data['debit_in'] = 'N/A'
                    host_data['debit_out'] = 'N/A'
                    
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
    
    def _get_bandwidth_for_host(self, ip):
        """
        Récupère le débit pour un hôte (en utilisant le cache).
        Cette fonction s'exécute de manière synchrone pour éviter les problèmes avec Flask.
        """
        try:
            # Créer une boucle asyncio temporaire pour la requête SNMP
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Récupérer les données de trafic actuelles
            current_data = loop.run_until_complete(
                snmp_helper.get_interface_traffic(ip, interface_index=1)
            )
            
            loop.close()
            
            if current_data is None:
                return {'in': '-', 'out': '-'}
            
            # Récupérer les données précédentes du cache
            previous_data = self.traffic_cache.get(ip)
            
            # Sauvegarder les données actuelles dans le cache
            self.traffic_cache[ip] = current_data
            
            # Si pas de données précédentes, attendre le prochain cycle
            if previous_data is None:
                return {'in': '-', 'out': '-'}
            
            # Calculer le débit
            bandwidth = snmp_helper.calculate_bandwidth(current_data, previous_data)
            
            if bandwidth:
                return {
                    'in': f"{bandwidth['in_mbps']:.2f} Mbps",
                    'out': f"{bandwidth['out_mbps']:.2f} Mbps"
                }
            
            return {'in': '-', 'out': '-'}
            
        except Exception as e:
            logger.debug(f"Erreur récupération débit pour {ip}: {e}")
            return {'in': '-', 'out': '-'}
    
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

