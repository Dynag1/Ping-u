import asyncio
import platform
import re
import sys
from PySide6.QtCore import QObject, Signal, QThread, Qt
from PySide6.QtGui import QStandardItem, QColor, QBrush
import src.var as var
from src.utils.logger import get_logger
from src.utils.colors import AppColors

# Import optionnel de SNMP (peut échouer dans l'exécutable PyInstaller)
try:
    from src.utils.snmp_helper import snmp_helper
    from src.utils.ups_monitor import ups_monitor
    SNMP_AVAILABLE = True
except ImportError as e:
    logger = get_logger(__name__)
    logger.warning(f"SNMP non disponible: {e}")
    snmp_helper = None
    ups_monitor = None
    SNMP_AVAILABLE = False

logger = get_logger(__name__)

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
        """Lance les pings par lots de 20 pour maximiser la stabilité avec SNMP."""
        batch_size = 20  # Réduit pour garantir la stabilité avec requêtes SNMP
        for i in range(0, len(ips), batch_size):
            if not self.is_running:
                break
            batch = ips[i:i + batch_size]
            # Lance les pings en parallèle
            tasks = [self.ping_host(ip) for ip in batch]
            await asyncio.gather(*tasks)

    async def ping_host(self, ip):
        """Ping un hôte spécifique de manière asynchrone via le système."""
        if not self.is_running:
            return

        latency = 500.0  # Valeur par défaut (Timeout/Erreur)
        
        try:
            # Commande selon l'OS
            if self.system == "windows":
                # -n 2 : deux pings pour confirmer la perte et éviter les faux positifs
                # -w 2000 : timeout 2000ms
                cmd = ["ping", "-n", "2", "-w", "2000", ip]
            else:
                # -c 2 : deux pings
                # -W 2 : timeout 2s
                # Utiliser le chemin complet de ping pour éviter les problèmes de permissions
                cmd = ["/bin/ping", "-c", "2", "-W", "2", ip]

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
                    logger.debug(f"Ping OK (TTL présent) mais latence illisible pour {ip}. Forcé à 10ms.")
            else:
                latency = 500.0
                # logger.debug(f"Ping échoué pour {ip}")

        except Exception as e:
            logger.debug(f"Erreur ping {ip}: {e}")
            latency = 500.0

        # Interrogation SNMP pour la température uniquement (optimisé pour beaucoup d'équipements)
        # Les débits sont récupérés par le serveur web à la demande (non-bloquant)
        temperature = None
        bandwidth = None
        # La récupération SNMP est maintenant gérée par le SNMPWorker dédié
        
        # Emission du résultat
        color = AppColors.get_latency_color(latency)
        self.result_signal.emit(ip, latency, color, temperature, bandwidth)
        
        # Mise à jour des listes (HS/OK)
        self.update_lists(ip, latency)

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

    def update_lists(self, ip, latency):
        try:
            # Ne pas mettre à jour les listes d'alertes si l'hôte est exclu
            # Note : get_all_ips filtre déjà les exclus, donc ce code ne devrait pas être atteint pour eux
            # Mais on garde la logique de base ici
            
            if latency == 500:
                self.list_increment(var.liste_hs, ip)
                self.list_increment(var.liste_mail, ip)
                self.list_increment(var.liste_telegram, ip)
            else:
                self.list_ok(var.liste_hs, ip)
                self.list_ok(var.liste_mail, ip)
                self.list_ok(var.liste_telegram, ip)
        except Exception as e:
            logger.error(f"Erreur update lists {ip}: {e}")

    def list_increment(self, liste, ip):
        if ip in liste:
            current_count = int(liste[ip])
            # Ne jamais incrémenter les états spéciaux (10 = alerte envoyée, 20 = retour OK détecté)
            if current_count >= 10:
                return
            # Incrémenter seulement si on n'a pas atteint le seuil
            target_hs = int(var.nbrHs)
            if current_count < target_hs:
                liste[ip] += 1
                logger.debug(f"Compteur incrémenté pour {ip}: {current_count} -> {liste[ip]} (Seuil: {target_hs})")
            else:
                logger.debug(f"Compteur max atteint pour {ip}: {current_count} (Seuil: {target_hs})")
        else:
            liste[ip] = 1
            logger.debug(f"Compteur initialisé pour {ip}: 1 (Seuil: {int(var.nbrHs)})")

    def list_ok(self, liste, ip):
        if ip in liste:
            if liste[ip] == 10:
                liste[ip] = 20
            else:
                liste.pop(ip, None)


class PingManager(QObject):
    def __init__(self, tree_model):
        super().__init__()
        self.tree_model = tree_model
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
            # Si pas d'IPs, on attend quand même
            # On utilise QTimer.singleShot
            from PySide6.QtCore import QTimer
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
        if var.tourne:
            from PySide6.QtCore import QTimer
            # On attend le délai configuré avant la prochaine vague
            # Note: var.delais est en secondes
            delay_ms = max(1, int(var.delais)) * 1000
            QTimer.singleShot(delay_ms, self.schedule_next_run)

    def get_all_ips(self):
        """Récupère toutes les IPs du modèle, y compris les exclues."""
        ips = []
        for row in range(self.tree_model.rowCount()):
            # On inclut TOUTES les IPs, même exclues, pour le ping
            item = self.tree_model.item(row, 1)
            if item:
                ips.append(item.text())
        return ips

    def handle_result(self, ip, latency, color, temperature, bandwidth):
        """Met à jour l'interface avec le résultat."""
        row = self.find_item_row(ip)
        if row == -1:
            return

        # Vérifier si l'hôte est exclu
        is_excluded = False
        item_excl = self.tree_model.item(row, 9)
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
                    # Afficher la latence réelle mais avec un indicateur "Exclu"
                    latency_text = f"{latency:.1f} ms" if latency < 500 else "HS"
                    item.setText(f"{latency_text}")
                else:
                    item.setText(f"{latency:.1f} ms" if latency < 500 else "HS")
            elif col == 6:  # Colonne Température (sera mis à jour par le thread SNMP séparé)
                pass # Ne rien faire ici pour la température, géré par SNMPWorker
            
            # Colorie toute la ligne
            if is_excluded:
                # Changer la couleur du texte pour indiquer l'exclusion (gris)
                item.setForeground(QBrush(QColor("gray")))
                # Fond légèrement grisé aussi pour bien distinguer
                if latency < 500:
                    # Si en ligne, fond vert très pâle ou gris clair
                    item.setBackground(QBrush(QColor(240, 240, 240)))
                else:
                    # Si hors ligne, fond rouge très pâle
                    item.setBackground(QBrush(QColor(255, 240, 240)))
            else:
                item.setBackground(QBrush(QColor(color)))
                item.setForeground(QBrush(QColor("black")))

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
            logger.info("Cache SNMP nettoyé à l'arrêt du monitoring")

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
        logger.info(f"Démarrage du worker SNMP sur {self.system}")
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
        logger.info("Arrêt du worker SNMP demandé")
        self.is_running = False
        # Permettre un arrêt rapide en attendant le thread
        self.wait()

    async def run_loop(self):
        """Boucle principale SNMP avec délai fixe de 5 secondes."""
        logger.info("Début de la boucle principale SNMP")
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
        """Interroge les équipements SNMP."""
        tasks = []
        for ip in ips:
            if not self.is_running:
                break
            tasks.append(self.poll_host(ip))
        
        if tasks:
            await asyncio.gather(*tasks)

    async def poll_host(self, ip):
        """Interroge un hôte spécifique."""
        try:
            # Timeout optimisé
            temp = await asyncio.wait_for(
                snmp_helper.get_temperature(ip), 
                timeout=2.0
            )
            
            bandwidth = None
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
            
            if temp or bandwidth:
                self.snmp_update_signal.emit(ip, str(temp) if temp else "", bandwidth)
                
        except (asyncio.TimeoutError, Exception):
            pass

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
                    item_temp.setText(temp)
                break

    def on_worker_finished(self):
        """Appelé quand une vague de pings est terminée."""
        if var.tourne:
            from PySide6.QtCore import QTimer
            # On attend le délai configuré avant la prochaine vague
            # Note: var.delais est en secondes
            delay_ms = max(1, int(var.delais)) * 1000
            QTimer.singleShot(delay_ms, self.schedule_next_run)

    def get_all_ips(self):
        """Récupère toutes les IPs du modèle, y compris les exclues."""
        ips = []
        for row in range(self.tree_model.rowCount()):
            # On inclut TOUTES les IPs, même exclues, pour le ping
            # L'exclusion sera gérée lors du traitement du résultat (pas d'alerte, affichage "EXCLU")
            item = self.tree_model.item(row, 1)
            if item:
                ips.append(item.text())
        return ips

    def handle_result(self, ip, latency, color, temperature, bandwidth):
        """Met à jour l'interface avec le résultat."""
        row = self.find_item_row(ip)
        if row == -1:
            return

        # Vérifier si l'hôte est exclu
        is_excluded = False
        item_excl = self.tree_model.item(row, 9)
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
                    # Afficher la latence réelle mais avec un indicateur "Exclu"
                    latency_text = f"{latency:.1f} ms" if latency < 500 else "HS"
                    item.setText(f"{latency_text}")
                else:
                    item.setText(f"{latency:.1f} ms" if latency < 500 else "HS")
            elif col == 6:  # Colonne Température (sera mis à jour par le thread SNMP séparé)
                pass # Ne rien faire ici pour la température, géré par SNMPWorker
            
            # Colorie toute la ligne
            if is_excluded:
                # Changer la couleur du texte pour indiquer l'exclusion (gris)
                item.setForeground(QBrush(QColor("gray")))
                # Fond légèrement grisé aussi pour bien distinguer
                if latency < 500:
                    # Si en ligne, fond vert très pâle ou gris clair
                    item.setBackground(QBrush(QColor(240, 240, 240)))
                else:
                    # Si hors ligne, fond rouge très pâle
                    item.setBackground(QBrush(QColor(255, 240, 240)))
            else:
                item.setBackground(QBrush(QColor(color)))
                item.setForeground(QBrush(QColor("black")))

    def update_lists(self, ip, latency):
        # Vérifier si l'hôte est exclu avant de mettre à jour les listes d'alertes
        try:
            row = self.find_item_row(ip)
            if row != -1:
                item_excl = self.tree_model.item(row, 9)
                if item_excl and item_excl.text() == "x":
                    return # Pas d'alerte pour les exclus

            if latency == 500:
                self.list_increment(var.liste_hs, ip)
                self.list_increment(var.liste_mail, ip)
                self.list_increment(var.liste_telegram, ip)
            else:
                self.list_ok(var.liste_hs, ip)
                self.list_ok(var.liste_mail, ip)
                self.list_ok(var.liste_telegram, ip)
        except Exception as e:
            logger.error(f"Erreur update lists {ip}: {e}")

    def handle_ups_alert(self, ip, message):
        """Gère les alertes UPS et envoie les notifications."""
        logger.info(f"Alerte UPS reçue: {message}")
        
        # Import des modules d'alerte
        try:
            # Popup
            if var.popup:
                from PySide6.QtWidgets import QMessageBox
                from PySide6.QtCore import QMetaObject, Qt
                # Utiliser invokeMethod pour afficher le popup dans le thread principal
                # Note: On pourrait aussi utiliser un signal dédié vers MainWindow
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
