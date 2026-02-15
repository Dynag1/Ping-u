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
import sys
import os
try:
    from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for, send_from_directory, Blueprint
    from flask_socketio import SocketIO, emit
    from flask_cors import CORS
    import json
    import shutil
    import os
    import zipfile
    import io
    import datetime
    from src.notification_manager import NotificationManager
    from src.web.routes.notification_routes import notification_bp
       
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Classes factices Flask conservées ici car spécifiques au serveur web
    class Flask: 
        def __init__(self, *args, **kwargs): pass
        def route(self, *args, **kwargs): return lambda f: f
        def config(self): return {}
    class Blueprint:
        def __init__(self, *args, **kwargs): pass
        def route(self, *args, **kwargs): return lambda f: f
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

from src.utils.headless_compat import GUI_AVAILABLE, QObject, Signal, QStandardItem


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
    
    def __init__(self, main_window, port=9090, host_manager=None):
        super().__init__()
        self.main_window = main_window
        self.host_manager = host_manager
        self.port = port
        
        # Déterminer le chemin absolu des templates
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
        # Cache partagé pour les débits SNMP (référence au cache du PingManager)
        self.traffic_cache = {}
        self._bandwidth_cache = {}  # Cache des derniers débits calculés (IP -> {in_mbps, out_mbps})
        
        # Gestionnaire de notifications
        self.notification_manager = NotificationManager()
        
        # Scanner réseau
        self._network_scanner = None
        self._scan_thread = None
        if NETWORK_SCANNER_AVAILABLE:
            self._network_scanner = NetworkScanner()
            self._network_scanner.add_callback(self._on_device_discovered)
        
        # Passer les instances aux Blueprints via la config Flask
        self.app.config['WEB_SERVER'] = self
        self.app.config['MAIN_WINDOW'] = self.main_window
        
        self._setup_routes()
        self._setup_socketio()
        
    def _setup_routes(self):
        """Configuration des routes Flask via Blueprints"""
        from src.web.routes.main_routes import main_bp
        from src.web.routes.auth_routes import auth_bp
        from src.web.routes.admin_routes import admin_bp
        from src.web.routes.host_routes import host_bp
        from src.web.routes.api_routes import api_bp
        from src.web.routes.scan_routes import scan_bp
        from src.web.routes.settings_routes import settings_bp
        from src.web.routes.site_routes import site_bp
        from src.web.routes.backup_routes import backup_bp
        from src.web.routes.synoptic_routes import synoptic_bp
        from src.web.routes.log_routes import log_bp
        from src.web.routes.dashboard_routes import dashboard_bp

        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(auth_bp)
        self.app.register_blueprint(admin_bp)
        self.app.register_blueprint(host_bp)
        self.app.register_blueprint(api_bp)
        self.app.register_blueprint(scan_bp)
        self.app.register_blueprint(settings_bp)
        self.app.register_blueprint(site_bp)
        self.app.register_blueprint(backup_bp)
        self.app.register_blueprint(synoptic_bp)
        self.app.register_blueprint(log_bp)
        self.app.register_blueprint(dashboard_bp)
        self.app.register_blueprint(notification_bp)
        
        # Initialiser la variable globale dans notification_routes
        import src.web.routes.notification_routes as nr
        nr.notification_manager = self.notification_manager

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
        """Extrait les données du HostManager avec filtrage optionnel par site"""
        hosts = []
        try:
            from src import var
            
            # Utilisation du HostManager (Thread-Safe)
            if self.host_manager:
                all_hosts = self.host_manager.get_all_hosts()
            else:
                logger.error("HostManager non initialisé dans WebServer")
                return []
            
            for host in all_hosts:
                try:
                    ip = host.get('ip', '')
                    if not ip: continue
                    
                    site = host.get('site', '')
                    
                    # Filtrage par site si activé
                    if apply_filter and var.site_filter:
                         if site not in var.site_filter:
                             # Vérifier si l'hôte a un site qui correspond
                             continue
                    
                    latence_text = host.get('latence', 'N/A')
                    
                    # Calculer la couleur de latence
                    latency_color = self._get_latency_color(latence_text)
                    
                    host_data = host.copy() # Copie pour ne pas modifier l'original dans HostManager
                    host_data['latency_color'] = latency_color
                    
                    # Récupération des débits depuis le cache (non bloquant)
                    bandwidth = self._get_cached_bandwidth(ip)
                    host_data['debit_in'] = bandwidth['in']
                    host_data['debit_out'] = bandwidth['out']
                    
                    # Assurer que les champs manquants sont présents
                    for field in ['nom', 'mac', 'port', 'temp', 'suivi', 'commentaire', 'excl']:
                        if field not in host_data:
                            host_data[field] = ''
                            
                    hosts.append(host_data)
                    
                except Exception as row_error:
                    logger.error(f"Erreur traitement host dans _get_hosts_data: {row_error}")
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
            if self.host_manager:
                return len(self.host_manager.get_all_hosts())
            return 0
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
                count = self._get_hosts_count()
                logger.info(f"Serveur web démarré avec {count} hôtes dans le HostManager")
            except Exception as e:
                logger.warning(f"Impossible de vérifier le nombre d'hôtes: {e}")
            
            local_ip = self._get_local_ip()
            local_ip = self._get_local_ip()
            logger.info(f"Serveur web accessible sur https://{local_ip}:{self.port}")
            logger.info(f"Accessible localement sur https://localhost:{self.port}")
            
            return True
        except Exception as e:
            logger.error(f"Erreur démarrage serveur web: {e}", exc_info=True)
            self.running = False
            return False
    
    def _ensure_ssl_certs(self):
        """Génère un certificat auto-signé si nécessaire"""

        try:
            # Répertoire pour stocker les certificats
            base_path = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(base_path)
            if getattr(sys, 'frozen', False):
                project_root = os.path.dirname(sys.executable)
                
            cert_dir = os.path.join(project_root, "bd", "certs")
            os.makedirs(cert_dir, exist_ok=True)
            
            cert_path = os.path.join(cert_dir, "cert.pem")
            key_path = os.path.join(cert_dir, "key.pem")
            
            if os.path.exists(cert_path) and os.path.exists(key_path):
                return (cert_path, key_path)
            
            logger.info("Génération d'un certificat SSL auto-signé...")
            
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            from cryptography.x509.oid import NameOID
            import datetime
            
            # Générer la clé privée
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Créer un certificat auto-signé
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, u"FR"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"France"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, u"Local"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Ping U"),
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                # Validité de 10 ans
                datetime.datetime.utcnow() + datetime.timedelta(days=3650)
            )
            
            # Ajouter SAN (Subject Alternative Name) pour localhost et l'IP locale
            alt_names = [x509.DNSName(u"localhost")]
            try:
                local_ip = self._get_local_ip()
                import ipaddress
                alt_names.append(x509.IPAddress(ipaddress.ip_address(local_ip)))
            except:
                pass
                
            cert = cert.add_extension(
                x509.SubjectAlternativeName(alt_names),
                critical=False,
            ).sign(key, hashes.SHA256(), default_backend())
            
            # Écrire le certificat
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
                
            # Écrire la clé privée
            with open(key_path, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info(f"Certificat SSL généré dans {cert_dir}")
            return (cert_path, key_path)
            
        except Exception as e:
            logger.error(f"Erreur génération certificats SSL: {e}", exc_info=True)
            return None

    def _run_server(self):
        """Exécute le serveur Flask-SocketIO"""
        try:
            # Désactiver les logs Werkzeug verbeux
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            
            for h in log.handlers[:]:
                log.removeHandler(h)
                
            class IgnoreWriteErrorFilter(logging.Filter):
                def filter(self, record):
                    return "write() before start_response" not in record.getMessage()
            
            log.addFilter(IgnoreWriteErrorFilter())
            
            # Vérifier si on doit forcer le HTTP (pour débug ou si HTTPS pose problème)
            # On cherche un fichier "no_ssl" dans le dossier de l'app ou dans bd/
            project_root = os.getcwd()
            force_http = os.path.exists(os.path.join(project_root, "no_ssl")) or \
                         os.path.exists(os.path.join(project_root, "bd", "no_ssl"))

            ssl_context = None
            if not force_http:
                ssl_paths = self._ensure_ssl_certs()
                if ssl_paths:
                    try:
                        import ssl
                        # Création d'un contexte SSL plus robuste que le simple tuple
                        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                        ssl_context.load_cert_chain(certfile=ssl_paths[0], keyfile=ssl_paths[1])
                        # Désactiver SSLv3 et TLSv1/1.1 pour la sécurité
                        ssl_context.options |= ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
                    except Exception as ssl_err:
                        logger.error(f"Erreur création contexte SSL: {ssl_err}")
                        ssl_context = None

            if ssl_context:
                logger.info("Démarrage du serveur Web en HTTPS")
                # Utiliser host='0.0.0.0' pour écouter sur toutes les interfaces
                self.socketio.run(self.app, 
                                host='0.0.0.0',
                                port=self.port, 
                                debug=False, 
                                allow_unsafe_werkzeug=True,
                                use_reloader=False,
                                ssl_context=ssl_context)
            else:
                mode = "forcé par l'utilisateur" if force_http else "échec SSL"
                logger.warning(f"Démarrage en HTTP standard ({mode})")
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
            s.settimeout(2)  # Ajouter un timeout pour éviter de bloquer
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
            'local': f'https://localhost:{self.port}',
            'network': f'https://{local_ip}:{self.port}'
        }

