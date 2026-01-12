import asyncio
import platform
import re
import sys
import src.var as var
from src.utils.logger import get_logger
from src.utils.colors import AppColors

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
try:
    from PySide6.QtCore import QObject, Signal, QThread, Qt, QTimer
    from PySide6.QtGui import QStandardItem, QColor, QBrush
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    import threading
    
    class Signal: 
        """Signal fonctionnel pour mode headless"""
        def __init__(self, *args): 
            self._callbacks = []
        def emit(self, *args): 
            for callback in self._callbacks:
                try:
                    callback(*args)
                except Exception as e:
                    print(f"Signal emit error: {e}")
        def connect(self, callback): 
            self._callbacks.append(callback)
    
    class QObject: 
        pass
    
    class QThread:
        """QThread fonctionnel pour mode headless utilisant threading.Thread"""
        def __init__(self):
            self._thread = None
            self._running = False
            self.finished = Signal()
        
        def start(self):
            self._running = True
            self._thread = threading.Thread(target=self._run_wrapper, daemon=True)
            self._thread.start()
        
        def _run_wrapper(self):
            try:
                self.run()
            finally:
                self._running = False
                self.finished.emit()
        
        def run(self):
            """À surcharger dans les sous-classes"""
            pass
        
        def wait(self, timeout_ms=None):
            if self._thread:
                timeout_sec = timeout_ms / 1000 if timeout_ms else None
                self._thread.join(timeout=timeout_sec)
                return not self._thread.is_alive()
            return True
        
        def isRunning(self):
            return self._running
        
        def quit(self):
            self._running = False
        
        def stop(self):
            self._running = False
    
    class QStandardItem:
        def __init__(self, text=""): 
            self._text = str(text) if text else ""
            self._background = None
            self._foreground = None
            self._data = {}
            self._flags = 0
        def text(self): 
            return self._text
        def setText(self, text): 
            self._text = str(text)
        def setForeground(self, brush): 
            self._foreground = brush
        def setBackground(self, brush): 
            self._background = brush
        def background(self):
            return self._background
        def foreground(self):
            return self._foreground
        def setData(self, data, role=0):
            self._data[role] = data
        def data(self, role=0):
            return self._data.get(role)
        def flags(self):
            return self._flags
        def setFlags(self, flags):
            self._flags = flags
        def setEditable(self, editable):
            pass
    
    class QColor:
        def __init__(self, *args): pass
    
    class QBrush:
        def __init__(self, *args): pass
    
    class Qt:
        pass
    
    class QTimer:
        @staticmethod
        def singleShot(ms, callback):
            """Timer fonctionnel pour mode headless"""
            import threading
            timer = threading.Timer(ms / 1000, callback)
            timer.daemon = True
            timer.start()

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
    
    # Vérifier si c'est un nom de domaine (contient des lettres)
    # Les IPs contiennent uniquement des chiffres et des points
    # Pattern pour IPv4: \d+\.\d+\.\d+\.\d+
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, host):
        # C'est une IP valide, pas une URL
        return False
    
    # Si ce n'est pas une IP et contient des lettres, c'est probablement un domaine/URL
    return bool(re.search(r'[a-zA-Z]', host))


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
            batch_size = 20  # Réduit pour garantir la stabilité avec requêtes SNMP
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
                # Commande selon l'OS
                if self.system == "windows":
                    # -n 2 : deux pings pour confirmer la perte et éviter les faux positifs
                    # -w 2000 : timeout 2000ms
                    cmd = ["ping", "-n", "2", "-w", "2000", host]
                else:
                    # -c 2 : deux pings
                    # -W 2 : timeout 2s
                    # Utiliser le chemin complet de ping pour éviter les problèmes de permissions
                    cmd = ["/bin/ping", "-c", "2", "-W", "2", host]

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
                    # logger.debug(f"Ping échoué pour {host}")

            except Exception as e:
                logger.debug(f"Erreur ping {host}: {e}")
                latency = 500.0

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
                # Linux/Mac: time=XX.X ms
                match = re.search(r"time=(\d+\.?\d*)", output, re.IGNORECASE)
                if match:
                    return float(match.group(1))
        except Exception as e:
            logger.error(f"Erreur parsing latence: {e}")
        
        # Si on arrive ici, c'est qu'on a pas trouvé la latence
        logger.warning(f"Pas de latence trouvée pour cette sortie de ping:\n{output}")
        return 500.0


class PingManager(QObject):
    def __init__(self, tree_model, main_window=None):
        super().__init__()
        self.tree_model = tree_model
        self.main_window = main_window
        self.worker = None
        self.timer = None
        # Cache pour stocker les données de trafic entre les cycles
        self.traffic_cache = {}

    def start(self):
        """Démarre le cycle de ping."""
        logger.info("Démarrage AsyncPingManager")
        # On utilise un QTimer pour relancer la vague de pings régulièrement
        self.timer = QObject() # Dummy parent for timer if needed, but simple timer is fine
        
        # Initialiser le worker SNMP autonome
        if SNMP_AVAILABLE:
            self.snmp_worker = SNMPWorker(self.tree_model, self.traffic_cache)
            self.snmp_worker.start()
        
        self.schedule_next_run()

    def schedule_next_run(self):
        if not var.tourne:
            return

        # Récupération des IPs
        ips = self.get_all_ips()
        
        if not ips:
            # Si pas d'IPs, on attend quand même avec un timer non-bloquant
            # QTimer est déjà défini globalement (PySide6 ou factice)
            QTimer.singleShot(int(var.delais) * 1000, self.schedule_next_run)
            return

        # Lancement du worker
        self.worker = AsyncPingWorker(ips, self.traffic_cache)
        self.worker.result_signal.connect(self.handle_result)
        self.worker.ups_alert_signal.connect(self.handle_ups_alert)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.start()

    def on_worker_finished(self):
        """Appelé quand une vague de pings est terminée."""
        # Broadcaster les mises à jour aux clients web (mode headless)
        if not GUI_AVAILABLE and self.main_window:
            try:
                if hasattr(self.main_window, 'web_server') and self.main_window.web_server:
                    self.main_window.web_server.broadcast_update()
            except Exception as e:
                logger.debug(f"Erreur broadcast: {e}")
        
        if var.tourne:
            # Délai avant la prochaine vague (non-bloquant)
            # QTimer est déjà défini globalement (PySide6 ou factice)
            delay_ms = max(1, int(var.delais)) * 1000
            QTimer.singleShot(delay_ms, self.schedule_next_run)

    def get_all_ips(self):
        """Récupère toutes les IPs du modèle, filtrées par sites actifs si définis."""
        ips_set = set()  # Utiliser un set pour éviter les doublons
        
        for row in range(self.tree_model.rowCount()):
            item = self.tree_model.item(row, 1)
            if item:
                ip_text = item.text().strip()
                if not ip_text:
                    continue
                
                # Filtrage par sites actifs si définis
                if var.sites_actifs:
                    site_item = self.tree_model.item(row, 8)  # Colonne Site
                    host_site = site_item.text().strip() if site_item else ''
                    
                    # Ne surveiller que les hôtes des sites actifs
                    if host_site not in var.sites_actifs:
                        continue
                
                ips_set.add(ip_text)
        
        return list(ips_set)

    def handle_result(self, ip, latency, color, temperature, bandwidth):
        """Met à jour l'interface avec le résultat."""
        row = self.find_item_row(ip)
        if row == -1:
            return

        # Vérifier si l'hôte est exclu (colonne 10)
        is_excluded = False
        item_excl = self.tree_model.item(row, 10)
        if item_excl and item_excl.text() == "x":
            is_excluded = True

        # Met à jour toutes les colonnes
        for col in range(self.tree_model.columnCount()):
            item = self.tree_model.item(row, col)
            # Crée l'item si inexistant
            if not item:
                item = QStandardItem()
                self.tree_model.setItem(row, col, item)
            
            # Applique la couleur et le texte selon la colonne
            if col == 5:  # Colonne Latence
                if is_excluded:
                    latency_text = f"{latency:.1f} ms" if latency < 500 else "HS"
                    item.setText(f"{latency_text}")
                else:
                    item.setText(f"{latency:.1f} ms" if latency < 500 else "HS")
            elif col == 6:  # Colonne Température (sera mis à jour par le thread SNMP séparé)
                pass # Ne rien faire ici pour la température, géré par SNMPWorker
            
            # Colorie toute la ligne (seulement si GUI disponible)
            if GUI_AVAILABLE:
                if is_excluded:
                    item.setForeground(QBrush(QColor("gray")))
                    if latency < 500:
                        item.setBackground(QBrush(QColor(240, 240, 240)))
                    else:
                        item.setBackground(QBrush(QColor(255, 240, 240)))
                else:
                    item.setBackground(QBrush(QColor(color)))
                    item.setForeground(QBrush(QColor("black")))
        
        # Mise à jour des listes (HS/OK) via le gestionnaire principal (thread-safe)
        self.update_lists(ip, latency)

    def update_lists(self, ip, latency):
        # Vérifier si l'hôte est exclu
        is_excluded = False
        try:
            row = self.find_item_row(ip)
            if row != -1:
                item_excl = self.tree_model.item(row, 10)  # Colonne 10 = Excl
                if item_excl and item_excl.text() == "x":
                    is_excluded = True

            # TOUJOURS mettre à jour liste_stats (même pour les hôtes exclus)
            # Les alertes sont bloquées pour les exclus, mais pas les statistiques
            # FIX: Utiliser >= 500 au lieu de == 500 pour capturer tous les cas d'échec
            if latency >= 500:
                # Stats toujours mises à jour
                self.list_increment(var.liste_stats, ip, log=False)
                # Alertes uniquement pour les non-exclus
                if not is_excluded:
                    self.list_increment(var.liste_hs, ip, log=True)
                    self.list_increment(var.liste_mail, ip, log=False)
                    self.list_increment(var.liste_telegram, ip, log=False)
            else:
                # Stats toujours mises à jour
                self.list_ok(var.liste_stats, ip)
                # Alertes uniquement pour les non-exclus
                if not is_excluded:
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
            # Ne jamais incrémenter les états spéciaux (10 = alerte envoyée, 20 = retour OK détecté)
            if current_count >= 10:
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
            if current_value < 10 and current_value > int(var.nbrHs):
                logger.error(f"[PING] {host_type} {ip}: ERREUR - compteur {current_value} > nbrHs {var.nbrHs}, réinitialisation à {var.nbrHs}")
                liste[ip] = int(var.nbrHs)

    def list_ok(self, liste, ip):
        if ip in liste:
            current_value = int(liste[ip])
            logger.debug(f"[PING] list_ok({ip}): valeur actuelle={current_value}, liste={liste.__class__.__name__}")
            if current_value == 10:
                # Alerte HS envoyée, marquer pour notification de retour
                liste[ip] = 20
                logger.info(f"[PING] {ip}: hôte revenu en ligne, marqué 20 pour notification de retour")
            elif current_value == 20:
                # Notification de retour en attente, ne pas supprimer !
                logger.debug(f"[PING] {ip}: notification de retour en attente, on garde la valeur 20")
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

    def find_item_row(self, ip):
        """Trouve la ligne correspondant à l'IP."""
        # Optimisation possible : garder un cache IP -> Row
        for row in range(self.tree_model.rowCount()):
            item = self.tree_model.item(row, 1)
            if item and item.text() == ip:
                return row
        return -1

    def stop(self):
        """Arrête le cycle et nettoie le cache SNMP."""
        logger.info("Arrêt AsyncPingManager")
        if hasattr(self, '_timer_ref') and self._timer_ref:
            self._timer_ref.stop()
        
        # Arrêter le worker SNMP
        if hasattr(self, 'snmp_worker') and self.snmp_worker:
            self.snmp_worker.stop()
            self.snmp_worker.wait(2000)
            self.snmp_worker = None
        
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            # Attendre maximum 5 secondes que le thread se termine
            if not self.worker.wait(5000):  # 5000 ms = 5 secondes
                logger.warning("Le thread de ping n'a pas pu s'arrêter proprement dans le délai imparti")
                # Forcer l'arrêt si nécessaire
                self.worker.quit()
                self.worker.wait(1000)  # Attendre encore 1 seconde
            else:
                logger.info("Thread de ping arrêté proprement")
        
        # Nettoyer le cache SNMP à l'arrêt (force une nouvelle détection au prochain démarrage)
        if SNMP_AVAILABLE and snmp_helper:
            snmp_helper.clear_cache()
            logger.debug("Cache SNMP nettoyé")

class SNMPWorker(QThread):
    """Worker autonome pour la mise à jour SNMP toutes les 5 secondes"""
    
    snmp_update_signal = Signal(str, str, object)  # ip, temp, bandwidth

    def __init__(self, tree_model, traffic_cache):
        super().__init__()
        self.tree_model = tree_model
        self.traffic_cache = traffic_cache
        self.is_running = True
        self.system = platform.system().lower()
        # Connecter le signal à une méthode locale (astuce pour thread-safety)
        self.snmp_update_signal.connect(self.apply_update)

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
        logger.debug("Boucle SNMP démarrée")
        while self.is_running:
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Récupérer les IPs (doit être fait de manière thread-safe si possible, ou au début)
                # Note: Accéder au modèle Qt depuis un autre thread est risqué, mais en lecture seule ça passe souvent
                # Idéalement, on devrait passer la liste des IPs via un signal ou une queue
                ips = self.get_all_ips_safe()
                
                if ips:
                    await self.snmp_poll(ips)
                
                # Calculer le temps restant pour atteindre 5 secondes
                elapsed = asyncio.get_event_loop().time() - start_time
                sleep_time = max(0.1, 5.0 - elapsed)
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Erreur cycle SNMP: {e}")
                await asyncio.sleep(5)

    def get_all_ips_safe(self):
        # Cette méthode est appelée depuis le thread, attention aux accès concurrents
        # Pour faire simple ici, on suppose que la liste ne change pas trop souvent
        ips = []
        try:
            count = self.tree_model.rowCount()
            for row in range(count):
                item = self.tree_model.item(row, 1)
                if item:
                    ips.append(item.text())
        except:
            pass
        return ips

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
                
                # Enregistrer dans l'historique pour les graphiques
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

    def apply_update(self, ip, temp, bandwidth):
        """Mise à jour thread-safe via signal."""
        for row in range(self.tree_model.rowCount()):
            item = self.tree_model.item(row, 1)
            if item and item.text() == ip:
                # Mise à jour Température
                if temp:
                    item_temp = self.tree_model.item(row, 6)
                    if not item_temp:
                        item_temp = QStandardItem()
                        self.tree_model.setItem(row, 6, item_temp)
                    
                    item_temp.setText(f"{temp}°C")
                    
                    # Gestion de la couleur de fond pour la température
                    try:
                        temp_val = float(temp)
                        if GUI_AVAILABLE:
                            from PySide6.QtGui import QColor, QBrush
                            if temp_val >= var.tempSeuil:
                                item_temp.setBackground(QBrush(QColor(AppColors.ROUGE_PALE)))
                            elif temp_val >= var.tempSeuilWarning:
                                item_temp.setBackground(QBrush(QColor(AppColors.ORANGE_PALE)))
                            else:
                                # Fond normal (blanc ou transparent selon le thème, ici on met transparent)
                                item_temp.setBackground(QBrush(Qt.NoBrush))
                    except (ValueError, TypeError):
                        pass
                break
