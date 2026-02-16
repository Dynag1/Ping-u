import time
import asyncio
import platform
import re
import sys
import subprocess
import shutil
import src.var as var
from src.utils.logger import get_logger
from src.utils.colors import AppColors
from src.database import get_host_notification_settings

# Initialize logger first
logger = get_logger(__name__)

# Import HTTP Checker pour la surveillance de sites web
try:
    from src.utils.http_checker import http_checker
    HTTP_CHECKER_AVAILABLE = True
    logger.debug("HTTP Checker chargé avec succès pour la surveillance de sites web")
except ImportError as e:
    logger.warning(f"HTTP checker non disponible: {e}")
    http_checker = None
    HTTP_CHECKER_AVAILABLE = False

# Imports PySide6 conditionnels
from src.utils.headless_compat import (
    GUI_AVAILABLE, QObject, Signal, QThread, Qt, QTimer,
    QStandardItem, QColor, QBrush
)


logger = get_logger(__name__)

# Import du parser d'URL pour gérer les ports
try:
    from src.utils.url_parser import parse_host_port
    URL_PARSER_AVAILABLE = True
except ImportError:
    URL_PARSER_AVAILABLE = False
    logger.warning("URL parser non disponible")

# Fonction utilitaire pour détecter les URLs
def _is_url(host):
    """Détecte si la chaîne est une URL/domaine plutôt qu'une adresse IP."""
    if not host:
        return False
    
    # Vérifier si c'est explicitement une URL avec protocole
    if host.startswith('http://') or host.startswith('https://'):
        return True
    
    # Si un port est spécifié, parser pour extraire l'hôte
    if ':' in host and URL_PARSER_AVAILABLE:
        parsed = parse_host_port(host)
        host = parsed['host']
    
    # Strict check: URL must start with protocol
    # If just a hostname (e.g. 'google.com' or 'nas'), treat as ping target
    return host.startswith('http://') or host.startswith('https://')



async def check_tcp_port(host, port, timeout=2):
    """
    Vérifie la connectivité TCP sur un port spécifique.
    
    Args:
        host: Adresse IP ou nom d'hôte
        port: Port à tester
        timeout: Timeout en secondes
        
    Returns:
        float: Temps de réponse en ms si succès, 500.0 si échec
    """
    import time
    start_time = time.time()
    
    try:
        # Tenter une connexion TCP
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        
        # Fermer la connexion proprement
        writer.close()
        await writer.wait_closed()
        
        # Calculer le temps de réponse
        response_time = (time.time() - start_time) * 1000
        return round(response_time, 2)
        
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
        logger.debug(f"TCP check failed for {host}:{port}: {e}")
        return 500.0
    except Exception as e:
        logger.warning(f"Unexpected error in TCP check for {host}:{port}: {e}")
        return 500.0



# Import optionnel de SNMP (peut échouer dans l'exécutable PyInstaller)
try:
    from src.utils.snmp_helper import snmp_helper
    from src.utils.ups_monitor import ups_monitor
    SNMP_AVAILABLE = True
except ImportError as e:
    logger.warning(f"SNMP non disponible: {e}")
    snmp_helper = None
    ups_monitor = None
    SNMP_AVAILABLE = False

class AsyncPingWorker(QThread):
    """
    Thread dédié à l'exécution de la boucle d'événements asyncio.
    """
    result_signal = Signal(str, float, str, object, object)  # ip, latence, couleur, température, bandwidth
    ups_alert_signal = Signal(str, str)  # ip, message d'alerte UPS

    def __init__(self, ips, traffic_cache=None):
        super().__init__()
        self.ips = ips
        self.is_running = True
        self.system = platform.system().lower()
        # Cache pour stocker les données de trafic précédentes (pour calculer le débit)
        self.traffic_cache = traffic_cache if traffic_cache is not None else {}

    def run(self):
        """Point d'entrée du thread."""
        try:
            # Création et exécution de la boucle asyncio
            if self.system == "windows":
                # Configurer la politique globalement pour ce thread seulement si nécessaire
                # Note: set_event_loop_policy affecte le thread courant ou le process selon l'implémentation
                # Pour être sûr, on utilise le ProactorEventLoop directement
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.ping_all(self.ips))
            loop.close()
        except Exception as e:
            logger.error(f"Erreur boucle asyncio: {e}", exc_info=True)

    def stop(self):
        self.is_running = False

    async def ping_all(self, ips):
        """
        Lance les pings de manière optimisée :
        - Sites web (URLs) : testés séquentiellement pour éviter les pertes
        - Adresses IP : testées en parallèle par lots de 20 pour la performance
        """
        # Séparer les sites web des adresses IP
        websites = []
        ip_addresses = []
        
        for ip in ips:
            if self._is_url(ip):
                websites.append(ip)
            else:
                ip_addresses.append(ip)
        
        # 1. Tester les sites web de manière SÉQUENTIELLE (un par un)
        if websites:
            logger.info(f"Test séquentiel de {len(websites)} site(s) web...")
            for website in websites:
                if not self.is_running:
                    break
                await self.ping_host(website)
        
        # 2. Tester les adresses IP en PARALLÈLE par lots (comme avant)
        if ip_addresses:
            logger.debug(f"Test parallèle de {len(ip_addresses)} adresse(s) IP...")
            batch_size = 5  # Réduit pour éviter la surcharge et les faux positifs (HS alors que connecté)
            for i in range(0, len(ip_addresses), batch_size):
                if not self.is_running:
                    break
                batch = ip_addresses[i:i + batch_size]
                # Lance les pings en parallèle
                tasks = [self.ping_host(ip) for ip in batch]
                await asyncio.gather(*tasks)

    async def ping_host(self, ip):
        """Ping un hôte spécifique de manière asynchrone via le système ou HTTP pour les sites web."""
        if not self.is_running:
            return

        latency = 500.0  # Valeur par défaut (Timeout/Erreur)
        original_address = ip
        
        # Parser l'adresse pour extraire l'hôte et le port si présent
        parsed = None
        if URL_PARSER_AVAILABLE:
            parsed = parse_host_port(ip)
            host = parsed['host']
            port = parsed['port']
            has_custom_port = parsed['has_port']
        else:
            host = ip
            port = None
            has_custom_port = False
        
        # Détecter si c'est un site web (URL) au lieu d'une IP
        is_website = self._is_url(original_address)
        
        # Cas 1: URL avec protocole (http:// ou https://) -> HTTP checker
        if is_website and HTTP_CHECKER_AVAILABLE and http_checker:
            # Mode site web: utiliser HTTP checker
            try:
                logger.info(f"[HTTP] Vérification du site web: {original_address}")
                result = await http_checker.check_website(original_address)
                
                logger.info(f"[HTTP] {original_address} - Résultat: success={result['success']}, status={result.get('status_code')}, time={result.get('response_time_ms')}ms, error={result.get('error')}")
                
                if result['success']:
                    # Site accessible, utiliser le temps de réponse
                    latency = result['response_time_ms']  # Déjà en ms
                    logger.info(f"[HTTP] ✓ Site web {original_address}: HTTP {result.get('status_code', 'OK')} - {latency:.1f} ms")
                else:
                    # Site inaccessible
                    latency = 500.0
                    logger.warning(f"[HTTP] ✗ Site web {original_address} inaccessible: {result.get('error', 'Unknown')} (status: {result.get('status_code', 'N/A')})")
            except Exception as e:
                logger.error(f"[HTTP] Exception lors de la vérification de {original_address}: {e}", exc_info=True)
                latency = 500.0
        
        # Cas 2: IP ou domaine avec port personnalisé -> TCP check
        elif has_custom_port and port:
            try:
                logger.info(f"[TCP] Vérification TCP sur {host}:{port}")
                latency = await check_tcp_port(host, port, timeout=2)
                
                if latency < 500:
                    logger.info(f"[TCP] ✓ Port {port} ouvert sur {host} - {latency:.1f} ms")
                else:
                    logger.warning(f"[TCP] ✗ Port {port} fermé/inaccessible sur {host}")
            except Exception as e:
                logger.error(f"[TCP] Exception lors de la vérification de {host}:{port}: {e}", exc_info=True)
                latency = 500.0
        
        # Cas 3: IP ou domaine sans port -> ICMP ping classique
        else:
            # Mode ICMP classique pour les IP
            try:
                # Résolution DNS préalable pour les noms d'hôtes
                # Cela évite que la commande ping n'échoue ou ne prenne trop de temps sur le DNS
                # et permet de préciser l'erreur
                target_ip = host
                try:
                    # Ne pas résoudre si c'est déjà une IP (simple check)
                    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', host):
                         import socket
                         target_ip = await asyncio.get_event_loop().run_in_executor(
                             None, 
                             socket.gethostbyname, 
                             host
                         )
                         logger.debug(f"Résolution DNS: {host} -> {target_ip}")
                except Exception as e:
                     logger.warning(f"Échec résolution DNS pour {host}: {e}")
                     # On continue quand même avec le nom, au cas où (ex: mDNS local, etc)
                     target_ip = host

                # Commande selon l'OS
                if self.system == "windows":
                    # -n 2 : deux pings
                    # -w 2000 : timeout 2000ms
                    # -4 : forcer IPv4
                    cmd = ["ping", "-n", "2", "-w", "2000", "-4", target_ip]
                else:
                    # -c 2 : deux pings
                    # -W 4 : timeout 4s (augmenté pour éviter les faux positifs)
                    # Utiliser le chemin complet pour éviter "No such file or directory"
                    ping_path = shutil.which("ping") or "/usr/bin/ping"
                    cmd = [ping_path, "-c", "2", "-W", "4", target_ip]

                # Création du sous-processus
                # Sur Windows, masquer la fenêtre CMD
                if self.system == "windows":
                    import subprocess
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )

                stdout, stderr = await process.communicate()
                
                # Décoder la sortie avec l'encodage approprié pour Windows français
                try:
                    # Windows français utilise souvent cp850 ou cp1252
                    if self.system == "windows":
                        output = stdout.decode('cp850', errors='ignore')
                    else:
                        output = stdout.decode('utf-8', errors='ignore')
                except:
                    output = stdout.decode('utf-8', errors='ignore')
                
                # Analyse robuste du résultat
                # On considère le ping réussi si :
                # 1. Le code de retour est 0 (standard)
                # 2. OU si on trouve "TTL=" dans la sortie (même si le code est != 0, ça arrive)
                # 3. ET qu'on n'a pas 100% de perte de paquets
                
                has_ttl = "TTL=" in output.upper() or "ttl=" in output.lower()
                
                # Recherche de perte de paquets (100% perte = HS)
                # Supporte français ("100% perte"), anglais ("100% packet loss"), etc.
                loss_match = re.search(r"(\d+)% [^,\n]*?(perte|loss)", output, re.IGNORECASE)
                is_100_percent_loss = False
                if loss_match and loss_match.group(1) == "100":
                    is_100_percent_loss = True

                if (process.returncode == 0 or has_ttl) and not is_100_percent_loss:
                    latency = self.parse_latency(output)
                    # Si le ping a réussi (TTL présent) mais parsing latence échoué (retourne 500)
                    if latency >= 500 and has_ttl:
                        # On force une latence "vivante" pour ne pas déclarer HS un hôte qui répond
                        latency = 10.0 
                        logger.debug(f"Ping OK (TTL présent) mais latence illisible pour {host}. Forcé à 10ms.")
                else:
                    latency = 500.0
                    logger.warning(f"Ping échoué pour {host} (RC={process.returncode}, TTL={'Oui' if has_ttl else 'Non'}, Loss100={'Oui' if is_100_percent_loss else 'Non'}) output:\n{output.strip()}")


            except Exception as e:
                logger.debug(f"Erreur ping {host}: {e}")
                latency = 500.0
            
            # Double vérification si échec (pour éviter les faux positifs)
            if latency >= 500.0 and self.is_running:
                try:
                    await asyncio.sleep(0.5)  # Petite pause avant retry
                    logger.debug(f"[RETRY] Seconde tentative pour {host}...")
                    
                    # Tentative plus robuste: 3 pings, timeout 3s
                    retry_cmd = list(cmd)
                    if self.system == "windows":
                        # Remplacer -n 2 par -n 3 et -w 2000 par -w 3000
                        try:
                            idx_n = retry_cmd.index("-n")
                            retry_cmd[idx_n+1] = "3"
                            idx_w = retry_cmd.index("-w")
                            retry_cmd[idx_w+1] = "3000"
                        except ValueError:
                            pass # Fallback à commande originale si options non trouvées
                    else:
                        # Remplacer -c 2 par -c 3 et -W 2 par -W 3
                        try:
                            idx_c = retry_cmd.index("-c")
                            retry_cmd[idx_c+1] = "3"
                            # Note: sur certaines distros, W est après c
                            if "-W" in retry_cmd:
                                idx_W = retry_cmd.index("-W")
                                retry_cmd[idx_W+1] = "3"
                        except ValueError:
                            pass

                    if self.system == "windows":
                        process = await asyncio.create_subprocess_exec(
                            *retry_cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:
                        process = await asyncio.create_subprocess_exec(
                            *retry_cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )


                    stdout, stderr = await process.communicate()
                    
                    try:
                        if self.system == "windows":
                            output = stdout.decode('cp850', errors='ignore')
                        else:
                            output = stdout.decode('utf-8', errors='ignore')
                    except:
                        output = stdout.decode('utf-8', errors='ignore')
                        
                    has_ttl = "TTL=" in output.upper() or "ttl=" in output.lower()
                    loss_match = re.search(r"(\d+)% [^,\n]*?(perte|loss)", output, re.IGNORECASE)
                    is_100_percent_loss = False
                    if loss_match and loss_match.group(1) == "100":
                        is_100_percent_loss = True

                    if (process.returncode == 0 or has_ttl) and not is_100_percent_loss:
                        latency = self.parse_latency(output)
                        if latency >= 500 and has_ttl:
                            latency = 10.0
                        logger.info(f"[RETRY] {host} récupéré au second ping ({latency}ms)")
                    else:
                        logger.debug(f"[RETRY] Echec confirmé pour {host} (output: {output.strip()})")

                        
                except Exception as e:
                    logger.error(f"Erreur retry ping {host}: {e}")

        # Interrogation SNMP pour la température uniquement (optimisé pour beaucoup d'équipements)
        # Les débits sont récupérés par le serveur web à la demande (non-bloquant)
        temperature = None
        bandwidth = None
        # La récupération SNMP est maintenant gérée par le SNMPWorker dédié
        
        # Emission du résultat
        color = AppColors.get_latency_color(latency)
        self.result_signal.emit(ip, latency, color, temperature, bandwidth)
    
    def _is_url(self, host):
        """Détecte si la chaîne est une URL/domaine plutôt qu'une adresse IP."""
        return _is_url(host)



    def parse_latency(self, output):
        """Extrait la latence de la sortie du ping."""
        try:
            if self.system == "windows":
                # Méthode 1: Recherche "temps=XX" ou "time=XX" (français/anglais)
                # Exemples: "temps=16 ms", "time=25ms", "temps<1ms"
                match = re.search(r"(?:temps|time)\s*[=<]\s*(\d+(?:\.\d+)?)", output, re.IGNORECASE)
                if match:
                    val = float(match.group(1))
                    logger.debug(f"Latence trouvée (Windows): {val} ms")
                    return val
                
                # Méthode 2: Chercher "Moyenne = XXms" dans les statistiques
                match_avg = re.search(r"Moyenne\s*=\s*(\d+(?:\.\d+)?)ms", output, re.IGNORECASE)
                if match_avg:
                    val = float(match_avg.group(1))
                    logger.debug(f"Latence trouvée (Moyenne): {val} ms")
                    return val
                
                # Méthode 3: Chercher "Average = XXms" (version anglaise)
                match_avg_en = re.search(r"Average\s*=\s*(\d+(?:\.\d+)?)ms", output, re.IGNORECASE)
                if match_avg_en:
                    val = float(match_avg_en.group(1))
                    logger.debug(f"Latence trouvée (Average): {val} ms")
                    return val
                
            else:
                # Linux/Mac: time=XX.X ms  ou  temps=XX.X ms (français)
                # On cherche les deux formats par sécurité. Supporte virgule ou point.
                match = re.search(r"(?:time|temps)=([0-9]+[.,]?[0-9]*)", output, re.IGNORECASE)
                if match:
                    val_str = match.group(1).replace(',', '.')
                    return float(val_str)

        except Exception as e:
            logger.error(f"Erreur parsing latence: {e}")
        
        # Si on arrive ici, c'est qu'on a pas trouvé la latence
        logger.warning(f"Pas de latence trouvée pour cette sortie de ping:\n{output}")
        return 500.0


class PingManager(QObject):
    result_signal = Signal(str, float, str, object, object)  # ip, latence, couleur, température, bandwidth
    finished_signal = Signal()  # Signal quand une vague est finie

    def __init__(self, get_ips_callback=None, main_window=None):
        super().__init__()
        self.get_ips_callback = get_ips_callback
        self.main_window = main_window
        self.worker = None
        self.timer = None
        # Cache pour stocker les données de trafic entre les cycles
        self.traffic_cache = {}
        # Cache pour stocker la dernière date de succès SNMP (timestamp)
        self.snmp_last_seen = {}
        self.snmp_worker = None

    def start(self):
        """Démarre le cycle de ping."""
        logger.info("Démarrage AsyncPingManager")
        
        # Initialiser le worker SNMP autonome
        if SNMP_AVAILABLE:
            logger.info("SNMP disponible, création du worker SNMP...")
            self.snmp_worker = SNMPWorker(self.traffic_cache, self.get_ips_callback)
            self.snmp_worker.snmp_update_signal.connect(self.handle_snmp_result)
            self.snmp_worker.start()
            logger.info("Worker SNMP démarré")
        else:
            logger.warning("SNMP NON disponible, worker SNMP non démarré")
        
        self.schedule_next_run()

    def schedule_next_run(self):
        if not var.tourne:
            return

        # Récupération des IPs via le callback
        ips = []
        if self.get_ips_callback:
            ips = self.get_ips_callback()
        
        if not ips:
            # Si pas d'IPs, on attend quand même
            QTimer.singleShot(max(1, int(var.delais)) * 1000, self.schedule_next_run)
            return

        # Lancement du worker
        self.worker = AsyncPingWorker(ips, self.traffic_cache)
        self.worker.result_signal.connect(self.handle_result)
        self.worker.ups_alert_signal.connect(self.handle_ups_alert)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self):
        """Appelé quand une vague de pings est terminée."""
        self.finished_signal.emit()
        
        # Broadcaster les mises à jour aux clients web (mode headless ou si serveur web actif)
        if self.main_window:
            try:
                if hasattr(self.main_window, 'web_server') and self.main_window.web_server:
                    self.main_window.web_server.broadcast_update()
            except Exception as e:
                logger.debug(f"Erreur broadcast: {e}")
        
        if var.tourne:
            delay_ms = max(1, int(var.delais)) * 1000
            QTimer.singleShot(delay_ms, self.schedule_next_run)

    def handle_result(self, ip, latency, color, temperature, bandwidth):
        """Relaye le résultat et met à jour les listes internes."""
        
        # Mise à jour des listes de statistiques/alertes (toujours stockées dans src.var)
        self.update_lists(ip, latency)
        
        # Gestion visuelle des échecs non confirmés
        visual_color = color
        
        # Si latence HS (>= 500) mais que le seuil n'est pas atteint (non confirmé)
        if latency >= 500.0:
            try:
                # Vérifier le compteur actuel
                current_count = var.liste_hs.get(ip, 0)
                target_hs = int(var.nbrHs)
                
                # Si le seuil est > 1 et qu'on n'a pas encore atteint le seuil
                if target_hs > 1 and current_count < target_hs:
                    # Afficher en ORANGE (Warning) au lieu de ROUGE pour signaler "en cours de vérification"
                    # Cela évite les "HS" rouges fugitifs qui n'apparaissent pas dans les logs
                    visual_color = AppColors.ORANGE_PALE
            except Exception as e:
                logger.debug(f"Erreur calcul couleur visuelle pour {ip}: {e}")

        # Relayage vers le signal principal pour que le contrôleur mette à jour le modèle
        self.result_signal.emit(ip, latency, visual_color, temperature, bandwidth)


    def handle_snmp_result(self, ip, temp, bandwidth):
        """Relaye les résultats SNMP."""
        # SNMP est DISSOCIÉ du statut HS - il fournit uniquement temp/bandwidth
        # Les alertes/HS sont gérés EXCLUSIVEMENT par le ping ICMP

        # Relayer les données SNMP pour affichage (température/bandwidth)
        color = ""  # Pas de couleur spécifique pour SNMP
        self.result_signal.emit(ip, -1.0, color, temp, bandwidth)


    def update_lists(self, ip, latency):
        # Les listes HS/Mail/Telegram dépendent de l'état d'exclusion.
        # Idéalement, PingManager ne devrait pas avoir à vérifier l'exclusion lui-même.
        # Mais pour l'instant on garde la compatibilité avec src.var.
        
        try:
            # Récupérer les paramètres de notification (cache ? ou direct DB)
            # Puisqu'on est dans le thread principal ou GUI, accès DB rapide (SQLite local)
            settings = get_host_notification_settings(ip)
            
            # Stats toujours mises à jour
            if latency >= 500:
                self.list_increment(var.liste_stats, ip, log=False)
                # Traitement des échecs ping - indépendant de SNMP
                self.list_increment(var.liste_hs, ip, log=True)
                
                # Vérifier si notifications activées pour cet hôte
                if settings.get('email', True):
                    self.list_increment(var.liste_mail, ip, log=False)
                else:
                    self.list_ok(var.liste_mail, ip)
                    
                if settings.get('telegram', True):
                    self.list_increment(var.liste_telegram, ip, log=False)
                else:
                    self.list_ok(var.liste_telegram, ip)
            else:
                self.list_ok(var.liste_stats, ip)
                self.list_ok(var.liste_hs, ip)
                self.list_ok(var.liste_mail, ip)
                self.list_ok(var.liste_telegram, ip)
        except Exception as e:
            logger.error(f"Erreur update lists {ip}: {e}")

    def list_increment(self, liste, ip, log=True):
        # Protection contre les IPs vides ou None
        if not ip or ip.strip() == "":
            return
        
        # Détecter si c'est un site web (URL)
        is_url = _is_url(ip)
        host_type = "URL" if is_url else "IP"
            
        if ip in liste:
            current_count = int(liste[ip])
            # Ne jamais incrémenter les états spéciaux (alerte envoyée ou retour OK)
            if current_count >= var.STATE_ALERT_SENT:
                if log:
                    logger.debug(f"[PING] {host_type} {ip}: état spécial {current_count}, pas d'incrémentation")
                return
            # Incrémenter seulement si on n'a pas atteint le seuil
            target_hs = int(var.nbrHs)
            if current_count < target_hs:
                liste[ip] += 1
                if log:
                    logger.info(f"[PING] {host_type} {ip}: compteur {current_count} -> {liste[ip]}/{target_hs}")
            else:
                if log:
                    logger.warning(f"[PING] {host_type} {ip}: compteur déjà au seuil {current_count}/{target_hs}, pas d'incrémentation")
        else:
            # IMPORTANT: Toujours initialiser à 1 pour le premier échec
            # Ne JAMAIS initialiser à nbrHs directement
            liste[ip] = 1
            if log:
                logger.info(f"[PING] {host_type} {ip}: premier échec 1/{int(var.nbrHs)}")
        
        # Vérification de sécurité: s'assurer que le compteur n'est jamais > nbrHs (sauf états spéciaux >= 10)
        if ip in liste:
            current_value = int(liste[ip])
            # Protection contre dépassement nbrHs (sauf états spéciaux)
            if current_value < var.STATE_ALERT_SENT and current_value > int(var.nbrHs):
                logger.error(f"[PING] {host_type} {ip}: ERREUR - compteur {current_value} > nbrHs {var.nbrHs}, réinitialisation à {var.nbrHs}")
                liste[ip] = int(var.nbrHs)

    def list_ok(self, liste, ip):
        if ip in liste:
            current_value = int(liste[ip])
            logger.debug(f"[PING] list_ok({ip}): valeur actuelle={current_value}, liste={liste.__class__.__name__}")
            if current_value == var.STATE_ALERT_SENT:
                # Alerte HS envoyée, marquer pour notification de retour
                liste[ip] = var.STATE_RECOVERY
                logger.info(f"[PING] {ip}: hôte revenu en ligne, marqué {var.STATE_RECOVERY} pour notification de retour")
            elif current_value == var.STATE_RECOVERY:
                # Notification de retour en attente, ne pas supprimer !
                logger.debug(f"[PING] {ip}: notification de retour en attente, on garde la valeur {var.STATE_RECOVERY}")
            else:
                # Compteur en cours (< nbrHs), supprimer car l'hôte répond à nouveau
                logger.debug(f"[PING] {ip}: supprimé de la liste (compteur était {current_value})")
                liste.pop(ip, None)
        else:
            logger.debug(f"[PING] list_ok({ip}): IP non présente dans la liste")

    def handle_ups_alert(self, ip, message):
        """Gère les alertes UPS et envoie les notifications."""
        logger.info(f"Alerte UPS reçue: {message}")
        
        # Import des modules d'alerte
        try:
            # Popup
            if var.popup:
                # On utilise simplement le logger pour le mode headless
                logger.info(f"Popup UPS: {message}")
            
            # Mail
            if var.mail:
                try:
                    from src import mail
                    mail.envoie(
                        subject=f"Alerte Onduleur - {ip}",
                        body=message
                    )
                    logger.info(f"Mail UPS envoyé pour {ip}")
                except Exception as e:
                    logger.error(f"Erreur envoi mail UPS: {e}", exc_info=True)
            
            # Telegram
            if var.telegram:
                try:
                    from src import telegram as tg
                    tg.envoie(message)
                    logger.info(f"Telegram UPS envoyé pour {ip}")
                except Exception as e:
                    logger.error(f"Erreur envoi Telegram UPS: {e}", exc_info=True)
                    
        except Exception as e:
            logger.error(f"Erreur gestion alerte UPS: {e}", exc_info=True)

    def stop(self):
        """Arrête le cycle et nettoie le cache SNMP."""
        logger.info("Arrêt AsyncPingManager")
        
        # Arrêter le worker SNMP
        if hasattr(self, 'snmp_worker') and self.snmp_worker:
            self.snmp_worker.stop()
            self.snmp_worker.wait(2000)
            self.snmp_worker = None
        
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            if not self.worker.wait(5000):
                logger.warning("Le thread de ping n'a pas pu s'arrêter proprement")
                self.worker.quit()
                self.worker.wait(1000)
            else:
                logger.info("Thread de ping arrêté proprement")
        
        if SNMP_AVAILABLE and snmp_helper:
            snmp_helper.clear_cache()
            logger.debug("Cache SNMP nettoyé")

class SNMPWorker(QThread):
    """Worker autonome pour la mise à jour SNMP toutes les 5 secondes"""
    
    snmp_update_signal = Signal(str, str, object)  # ip, temp, bandwidth

    def __init__(self, traffic_cache, get_ips_callback=None):
        super().__init__()
        self.traffic_cache = traffic_cache
        self.get_ips_callback = get_ips_callback
        self.is_running = True
        self.system = platform.system().lower()

    def run(self):
        """Point d'entrée du thread."""
        logger.debug(f"Worker SNMP démarré ({self.system})")
        try:
            # Création et exécution de la boucle asyncio
            if platform.system().lower() == "windows":
                # Configurer la politique globalement pour ce thread
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_loop())
            loop.close()
        except Exception as e:
            logger.error(f"Erreur boucle asyncio SNMP: {e}", exc_info=True)

    def stop(self):
        logger.debug("Arrêt worker SNMP")
        self.is_running = False
        # Permettre un arrêt rapide en attendant le thread
        self.wait()

    async def run_loop(self):
        """Boucle principale SNMP avec délai fixe de 5 secondes."""
        logger.info("Boucle SNMP démarrée")
        while self.is_running:
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Récupérer les IPs via le callback
                ips = []
                if self.get_ips_callback:
                    ips = self.get_ips_callback()
                
                if ips:
                    await self.snmp_poll(ips)
                
                elapsed = asyncio.get_event_loop().time() - start_time
                sleep_time = max(0.1, 5.0 - elapsed)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Erreur cycle SNMP: {e}")
                await asyncio.sleep(5)

    async def snmp_poll(self, ips):
        """Interroge les équipements SNMP par petits lots pour éviter la surcharge."""
        batch_size = 5  # Traiter 5 IPs à la fois max
        
        for i in range(0, len(ips), batch_size):
            if not self.is_running:
                break
            
            batch = ips[i:i + batch_size]
            tasks = [self.poll_host(ip) for ip in batch]
            
            try:
                # Gather avec return_exceptions pour ne pas bloquer sur les erreurs
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                logger.debug(f"Erreur batch SNMP: {e}")
            
            # Petite pause entre les batches pour ne pas surcharger
            if i + batch_size < len(ips):
                await asyncio.sleep(0.2)

    async def poll_host(self, ip):
        """Interroge un hôte spécifique avec gestion d'erreurs robuste."""
        if not self.is_running:
            return
        
        temp = None
        bandwidth = None
        
        try:
            # Température avec timeout court
            temp = await asyncio.wait_for(
                snmp_helper.get_temperature(ip), 
                timeout=2.0
            )
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.debug(f"Erreur SNMP temp {ip}: {e}")
        
        if not self.is_running:
            return
        
        try:
            # Bande passante avec timeout court
            previous_data = self.traffic_cache.get(ip)
            bandwidth_result = await asyncio.wait_for(
                snmp_helper.calculate_bandwidth(ip, interface_index=None, previous_data=previous_data),
                timeout=2.0
            )
            
            if bandwidth_result:
                bandwidth = {
                    'in_mbps': bandwidth_result['in_mbps'],
                    'out_mbps': bandwidth_result['out_mbps']
                }
                self.traffic_cache[ip] = bandwidth_result['raw_data']
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logger.debug(f"Erreur SNMP bandwidth {ip}: {e}")
        
        # Émettre les résultats si disponibles
        if temp or bandwidth:
            try:
                self.snmp_update_signal.emit(ip, str(temp) if temp else "", bandwidth)
                
                # Enregistrer dans l'historique
                try:
                    from src.monitoring_history import get_monitoring_manager
                    manager = get_monitoring_manager()
                    if temp:
                        manager.record_temperature(ip, temp)
                    if bandwidth:
                        manager.record_bandwidth(ip, bandwidth['in_mbps'], bandwidth['out_mbps'])
                except Exception as e:
                    logger.debug(f"Erreur enregistrement historique {ip}: {e}")
            except Exception as e:
                logger.debug(f"Erreur émission signal SNMP {ip}: {e}")
