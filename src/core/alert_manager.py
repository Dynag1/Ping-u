try:
    from PySide6.QtCore import QObject, QTimer, Signal
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    class QObject: pass
    
    class Signal:
        def __init__(self, *args):
            self._slots = []
        def connect(self, slot):
            self._slots.append(slot)
        def emit(self, *args):
            for slot in self._slots:
                try:
                    slot(*args)
                except Exception as e:
                    print(f"Signal emit error: {e}")

    class QTimer:
        def __init__(self):
            self._interval = 1000
            self._callback = None
            self._timer = None
            self._running = False
            self.timeout = self

        def connect(self, slot):
            self._callback = slot

        def start(self, ms=None):
            if ms is not None:
                self._interval = ms
            self.stop()
            self._running = True
            self._schedule()

        def stop(self):
            self._running = False
            if self._timer:
                self._timer.cancel()
                self._timer = None

        def setInterval(self, ms):
            self._interval = ms

        def interval(self):
            return self._interval

        def _schedule(self):
            if not self._running:
                return
            import threading
            self._timer = threading.Timer(self._interval / 1000.0, self._run_callback)
            self._timer.daemon = True
            self._timer.start()

        def _run_callback(self):
            if self._running and self._callback:
                try:
                    self._callback()
                except Exception:
                    pass
                self._schedule()

import threading
from src import thread_mail, thread_recap_mail, thread_telegram, var, db
from src.utils.logger import get_logger
from src.utils.colors import AppColors

logger = get_logger(__name__)

class AlertManager(QObject):
    """
    Gestionnaire d'alertes non-bloquant basé sur QTimer.
    Remplace l'ancien threadLancement.py.
    """
    
    popup_signal = Signal(str)

    def __init__(self, main_window, model):
        super().__init__()
        self.main_window = main_window
        self.model = model
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alerts)
        
        # Référence au thread mail recap pour éviter les doublons
        self.mail_recap_thread = None
        
        # Connecter le signal popup local au signal de la fenêtre principale
        self.popup_signal.connect(self.main_window.show_popup)

    def start(self):
        """Démarre la surveillance des alertes."""
        logger.info(f"Gestionnaire d'alertes démarré (seuil: {var.nbrHs})")
        self.check_mail_recap()
        
        # Démarrer le timer avec le délai configuré
        delay_ms = max(10, int(var.delais)) * 1000
        self.timer.start(delay_ms)

    def stop(self):
        """Arrête la surveillance et tous les threads associés."""
        self.timer.stop()
        
        # Attendre la fin du thread mail recap s'il existe
        if self.mail_recap_thread and self.mail_recap_thread.is_alive():
            logger.info("Attente fin du thread mail recap...")
            # Le thread s'arrêtera grâce à stop_event (signalé par main_controller)
            self.mail_recap_thread.join(timeout=2)
            if self.mail_recap_thread.is_alive():
                logger.warning("Thread mail recap n'a pas pu s'arrêter dans le délai imparti")
        self.mail_recap_thread = None
        
        logger.info("Arrêt du gestionnaire d'alertes")

    def check_alerts(self):
        """Vérifie périodiquement les alertes."""
        if not var.tourne:
            self.stop()
            return

        # Ajuster le timer si le délai a changé
        current_interval = self.timer.interval()
        new_interval = max(10, int(var.delais)) * 1000
        if current_interval != new_interval:
            self.timer.setInterval(new_interval)

        try:
            if var.popup:
                self.process_popup()
            if var.mail:
                self.process_mail()
            if var.telegram:
                self.process_telegram()
            if var.tempAlert:
                self.process_temp_alerts()
        except Exception as e:
            logger.error(f"Erreur vérification alertes: {e}", exc_info=True)

    def check_mail_recap(self):
        """Lance le thread de récapitulatif mail (évite les doublons)."""
        if var.tourne and var.mailRecap:
            # Vérifier si un thread mail recap est déjà en cours
            if self.mail_recap_thread and self.mail_recap_thread.is_alive():
                logger.debug("Thread mail recap déjà en cours, pas de nouveau lancement")
                return
            
            try:
                self.mail_recap_thread = threading.Thread(
                    target=thread_recap_mail.main, 
                    args=(self.main_window, self.model),
                    daemon=True,
                    name="MailRecapThread"
                )
                self.mail_recap_thread.start()
                logger.info("Thread mail recap lancé")
            except Exception as e:
                logger.error(f"Erreur lancement recap mail: {e}", exc_info=True)

    def process_popup(self):
        """Traite les alertes popup."""
        try:
            erase = []
            ip_hs = ""
            ip_ok = ""
            
            for key, value in list(var.liste_hs.items()):
                if int(value) == int(var.nbrHs):
                    ip_hs += f"{key}\n "
                    var.liste_hs[key] = 10
                elif int(value) == 20:
                    ip_ok += f"{key}\n "
                    erase.append(key)
            
            for cle in erase:
                var.liste_hs.pop(cle, None)
                
            if ip_hs:
                mess = self.main_window.tr("les hotes suivants sont HS : \n") + ip_hs
                self.popup_signal.emit(mess)
            if ip_ok:
                mess = self.main_window.tr("les hotes suivants sont OK : \n") + ip_ok
                self.popup_signal.emit(mess)
                
        except Exception as e:
            logger.error(f"Erreur process popup: {e}", exc_info=True)

    def process_mail(self):
        """Traite les alertes mail avec templates HTML modernes."""
        try:
            from src import email_sender
            
            erase = []
            hosts_down = []
            hosts_up = []
            
            # Log de diagnostic pour voir l'état des listes
            if var.liste_mail:
                logger.debug(f"[MAIL] État liste_mail: {dict(var.liste_mail)}")
            
            for key, value in list(var.liste_mail.items()):
                logger.debug(f"[MAIL] Vérification {key}: valeur={value} (type={type(value).__name__}), nbrHs={var.nbrHs}")
                
                if int(value) == int(var.nbrHs):
                    # Hôte qui vient de tomber
                    logger.info(f"Alerte mail: {key} HS")
                    nom = db.lireNom(key, self.model) or "Inconnu"
                    
                    # Récupérer les infos de l'hôte depuis le modèle
                    mac = ""
                    latence = "HS"
                    site = ""
                    for row in range(self.model.rowCount()):
                        item_ip = self.model.item(row, 1)
                        if item_ip and item_ip.text() == key:
                            mac_item = self.model.item(row, 3)
                            site_item = self.model.item(row, 8)
                            mac = mac_item.text() if mac_item else ""
                            site = site_item.text() if site_item else ""
                            break
                    
                    host_info = {
                        'ip': key,
                        'nom': nom,
                        'mac': mac,
                        'latence': latence,
                        'site': site
                    }
                    hosts_down.append(host_info)
                    var.liste_mail[key] = 10
                    
                elif int(value) == 20:
                    # Hôte qui revient en ligne
                    logger.info(f"[MAIL] Alerte retour détectée: {key} revient en ligne (valeur={value})")
                    nom = db.lireNom(key, self.model) or "Inconnu"
                    
                    # Récupérer les infos de l'hôte
                    mac = ""
                    latence = "OK"
                    site = ""
                    for row in range(self.model.rowCount()):
                        item_ip = self.model.item(row, 1)
                        if item_ip and item_ip.text() == key:
                            mac_item = self.model.item(row, 3)
                            latence_item = self.model.item(row, 5)
                            site_item = self.model.item(row, 8)
                            mac = mac_item.text() if mac_item else ""
                            latence = latence_item.text() if latence_item else "OK"
                            site = site_item.text() if site_item else ""
                            break
                    
                    host_info = {
                        'ip': key,
                        'nom': nom,
                        'mac': mac,
                        'latence': latence,
                        'site': site
                    }
                    hosts_up.append(host_info)
                    erase.append(key)
            
            for cle in erase:
                var.liste_mail.pop(cle, None)
            
            # Envoyer UN SEUL mail groupé si des alertes existent
            if hosts_down or hosts_up:
                logger.info(f"[MAIL] Envoi d'un mail groupé: {len(hosts_down)} HS, {len(hosts_up)} revenu(s)")
                threading.Thread(
                    target=email_sender.send_grouped_alert_email,
                    args=(hosts_down, hosts_up)
                ).start()
                
        except Exception as e:
            logger.error(f"Erreur process mail: {e}", exc_info=True)

    def process_telegram(self):
        """Traite les alertes Telegram."""
        try:
            erase = []
            ip_hs_text = ""
            ip_ok_text = ""
            send_msg = False
            
            message = self.main_window.tr("Alerte sur le site ") + var.nom_site + "\n \n"
            
            for key, value in list(var.liste_telegram.items()):
                if int(value) == int(var.nbrHs):
                    logger.info(f"Alerte Telegram: {key} HS")
                    nom = db.lireNom(key, self.model) or "Inconnu"
                    # Récupérer le site de l'hôte
                    site = ""
                    for row in range(self.model.rowCount()):
                        item_ip = self.model.item(row, 1)
                        if item_ip and item_ip.text() == key:
                            site_item = self.model.item(row, 8)
                            site = site_item.text() if site_item else ""
                            break
                    site_prefix = f"[{site}] " if site else ""
                    ip_hs_text += f"{site_prefix}{nom} : {key}\n"
                    var.liste_telegram[key] = 10
                elif int(value) == 20:
                    nom = db.lireNom(key, self.model) or "Inconnu"
                    # Récupérer le site de l'hôte
                    site = ""
                    for row in range(self.model.rowCount()):
                        item_ip = self.model.item(row, 1)
                        if item_ip and item_ip.text() == key:
                            site_item = self.model.item(row, 8)
                            site = site_item.text() if site_item else ""
                            break
                    site_prefix = f"[{site}] " if site else ""
                    ip_ok_text += f"{site_prefix}{nom} : {key}\n"
                    erase.append(key)
            
            for cle in erase:
                var.liste_telegram.pop(cle, None)
                
            if ip_hs_text:
                send_msg = True
                message += self.main_window.tr("les hotes suivants sont HS : \n") + ip_hs_text
                
            if ip_ok_text:
                send_msg = True
                message += self.main_window.tr("les hotes suivants sont OK : \n") + ip_ok_text
                
            if send_msg:
                threading.Thread(target=thread_telegram.main, args=(message,)).start()
                
        except Exception as e:
            logger.error(f"Erreur process telegram: {e}", exc_info=True)

    def process_temp_alerts(self):
        """Traite les alertes de température élevée."""
        try:
            seuil = int(var.tempSeuil)
            hosts_high_temp = []
            hosts_normal_temp = []
            
            # Parcourir tous les hôtes pour vérifier leur température
            for row in range(self.model.rowCount()):
                item_ip = self.model.item(row, 1)
                item_temp = self.model.item(row, 6)  # Colonne température
                
                if not item_ip or not item_temp:
                    continue
                    
                ip = item_ip.text()
                temp_text = item_temp.text()
                
                # Extraire la valeur numérique de la température
                try:
                    # Gérer les formats "45°C", "45", "45.5°C", etc.
                    temp_str = temp_text.replace('°C', '').replace('°', '').strip()
                    if not temp_str or temp_str == '-':
                        continue
                    temp = float(temp_str)
                except (ValueError, AttributeError):
                    continue
                
                # Vérifier si la température dépasse le seuil
                if temp >= seuil:
                    # Température élevée
                    if ip not in var.liste_temp_alert:
                        var.liste_temp_alert[ip] = 1
                    elif var.liste_temp_alert[ip] < 10:
                        # Première alerte (compteur = 1), on envoie
                        if var.liste_temp_alert[ip] == 1:
                            nom = db.lireNom(ip, self.model) or "Inconnu"
                            hosts_high_temp.append({
                                'ip': ip,
                                'nom': nom,
                                'temp': temp,
                                'seuil': seuil
                            })
                            logger.warning(f"🌡️ Alerte température: {ip} ({nom}) = {temp}°C (seuil: {seuil}°C)")
                            var.liste_temp_alert[ip] = 10  # Marquer comme alerté
                else:
                    # Température normale - retirer de la liste si présent
                    if ip in var.liste_temp_alert:
                        if var.liste_temp_alert[ip] == 10:
                            nom = db.lireNom(ip, self.model) or "Inconnu"
                            hosts_normal_temp.append({
                                'ip': ip,
                                'nom': nom,
                                'temp': temp
                            })
                            logger.info(f"🌡️ Température normalisée: {ip} ({nom}) = {temp}°C")
                        del var.liste_temp_alert[ip]
            
            # Envoyer les alertes
            if hosts_high_temp:
                self._send_temp_alerts(hosts_high_temp, 'high')
            if hosts_normal_temp:
                self._send_temp_alerts(hosts_normal_temp, 'normal')
                
        except Exception as e:
            logger.error(f"Erreur process temp alerts: {e}", exc_info=True)

    def _send_temp_alerts(self, hosts, alert_type):
        """Envoie les alertes température via les canaux configurés."""
        try:
            # Construire le message
            if alert_type == 'high':
                title = "🌡️ ALERTE TEMPÉRATURE ÉLEVÉE"
                hosts_text = "\n".join([f"  • {h['nom']} ({h['ip']}): {h['temp']}°C (seuil: {h['seuil']}°C)" for h in hosts])
            else:
                title = "✅ Température normalisée"
                hosts_text = "\n".join([f"  • {h['nom']} ({h['ip']}): {h['temp']}°C" for h in hosts])
            
            message = f"{title}\n{hosts_text}"
            
            # Popup
            if var.popup:
                self.popup_signal.emit(message)
            
            # Email
            if var.mail:
                try:
                    from src import email_sender
                    for host in hosts:
                        host_info = {
                            'ip': host['ip'],
                            'nom': host['nom'],
                            'temp': host['temp'],
                            'seuil': host.get('seuil', var.tempSeuil)
                        }
                        threading.Thread(
                            target=email_sender.send_temp_alert_email,
                            args=(host_info, alert_type)
                        ).start()
                except Exception as e:
                    logger.error(f"Erreur envoi email température: {e}")
            
            # Telegram
            if var.telegram:
                full_message = self.main_window.tr("Alerte sur le site ") + var.nom_site + "\n\n" + message
                threading.Thread(target=thread_telegram.main, args=(full_message,)).start()
                
        except Exception as e:
            logger.error(f"Erreur envoi alertes température: {e}", exc_info=True)
