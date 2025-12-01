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
        if latency < 500 and SNMP_AVAILABLE:
            try:
                # Timeout optimisé de 2 secondes pour la température
                temperature = await asyncio.wait_for(
                    snmp_helper.get_temperature(ip), 
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                pass
            
            # Récupération des débits réseau (avec filtrage intelligent et auto-détection interface)
            try:
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
                pass
        
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
            if current_count < int(var.nbrHs):
                liste[ip] += 1
        else:
            liste[ip] = 1

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
        # En fait, on peut utiliser startTimer du QObject ou un QTimer instance
        # Pour simplifier et éviter les problèmes de thread, on recrée le worker à chaque cycle
        # ou on utilise une boucle dans le worker.
        # Mieux : QTimer dans le main thread qui lance un worker 'one-shot' à chaque fois.
        
        self.schedule_next_run()

    def stop(self):
        """Arrête le cycle et nettoie le cache SNMP."""
        logger.info("Arrêt AsyncPingManager")
        if hasattr(self, '_timer_ref') and self._timer_ref:
            self._timer_ref.stop()
        
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

    def schedule_next_run(self):
        if not var.tourne:
            return

        # Récupération des IPs
        ips = self.get_all_ips()
        
        if not ips:
            # Si pas d'IPs, on attend quand même
            self._timer_ref = QThread.msleep(1000) # Non, ça bloque.
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
        """Récupère toutes les IPs du modèle."""
        ips = []
        for row in range(self.tree_model.rowCount()):
            item = self.tree_model.item(row, 1)
            if item:
                ips.append(item.text())
        return ips

    def handle_result(self, ip, latency, color, temperature, bandwidth):
        """Met à jour l'interface avec le résultat."""
        row = self.find_item_row(ip)
        if row == -1:
            return

        # Met à jour toutes les colonnes
        for col in range(self.tree_model.columnCount()):
            item = self.tree_model.item(row, col)
            # Crée l'item si inexistant
            if not item:
                item = QStandardItem()
                self.tree_model.setItem(row, col, item)
            # Applique la couleur et le texte selon la colonne
            if col == 5:  # Colonne Latence
                item.setText(f"{latency:.1f} ms" if latency < 500 else "HS")
            elif col == 6:  # Colonne Température
                if temperature is not None:
                    try:
                        # Convertir en float si c'est une string
                        temp_value = float(temperature)
                        item.setText(f"{temp_value:.1f}°C")
                    except (ValueError, TypeError):
                        # Si conversion échoue, afficher tel quel ou "-"
                        item.setText(str(temperature) if temperature else "-")
                else:
                    item.setText("-")
            # Colorie toute la ligne
            item.setBackground(QBrush(QColor(color)))

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
