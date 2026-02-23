from src.utils.headless_compat import QObject, Signal, QTimer, GUI_AVAILABLE

import threading
from src import thread_mail, thread_recap_mail, thread_telegram, var, db, email_sender
from src.utils.logger import get_logger
from src.utils.colors import AppColors
from src.notification_manager import NotificationManager

# Import du gestionnaire de statistiques de connexion
try:
    from src.connection_stats import stats_manager
    STATS_AVAILABLE = True
except ImportError as e:
    get_logger(__name__).warning(f"Stats de connexion non disponibles: {e}")
    stats_manager = None
    STATS_AVAILABLE = False

logger = get_logger(__name__)

class AlertManager(QObject):
    """
    Gestionnaire d'alertes non-bloquant basé sur QTimer.
    Remplace l'ancien threadLancement.py.
    """
    
    popup_signal = Signal(str)

    def __init__(self, main_window, get_host_metadata_callback=None, get_all_hosts_data_callback=None):
        super().__init__()
        self.main_window = main_window
        self.notification_manager = NotificationManager()
        self.get_host_metadata_callback = get_host_metadata_callback
        self.get_all_hosts_data_callback = get_all_hosts_data_callback
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_alerts)
        
        # Référence au thread mail recap pour éviter les doublons
        self.mail_recap_thread = None
        
        # Connecter le signal popup local au signal de la fenêtre principale (si dispo)
        if GUI_AVAILABLE and hasattr(self.main_window, 'show_popup'):
            self.popup_signal.connect(self.main_window.show_popup)

    def start(self):
        """Démarre la surveillance des alertes."""
        logger.info(f"Gestionnaire d'alertes démarré (seuil: {var.nbrHs})")
        
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
            # Toujours traiter les statistiques, quel que soit le mode d'alerte
            self.process_stats()
            
            if var.popup:
                self.process_popup()
            if var.mail:
                self.process_mail()
            if var.telegram:
                self.process_telegram()
            if var.tempAlert:
                self.process_temp_alerts()
            
            # Vérifier l'état du mail recap (lance le thread si activé et qu'il ne tourne pas)
            self.check_mail_recap()
            
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
                    args=(self.main_window, self.get_all_hosts_data_callback),
                    daemon=True,
                    name="MailRecapThread"
                )
                self.mail_recap_thread.start()
                logger.info("Thread mail recap lancé")
            except Exception as e:
                logger.error(f"Erreur lancement recap mail: {e}", exc_info=True)

    def _get_host_metadata(self, ip):
        """Récupère les métadonnées d'un hôte (nom, site, mac, latence, etc.) de manière sécurisée."""
        metadata = {}
        if self.get_host_metadata_callback:
            metadata = self.get_host_metadata_callback(ip) or {}
        return {
            'nom': metadata.get('nom') or "Inconnu",
            'site': metadata.get('site') or "",
            'mac': metadata.get('mac') or "",
            'latence': metadata.get('latence') or "OK"
        }

    def process_stats(self):
        """Enregistre les événements de déconnexion/reconnexion dans les statistiques.
        Utilise liste_stats qui est indépendante des listes d'alertes."""
        if not STATS_AVAILABLE or not stats_manager:
            return
        
        # Set pour tracker les IPs déjà enregistrées (éviter doublons)
        if not hasattr(self, '_stats_recorded_disconnects'):
            self._stats_recorded_disconnects = set()
        
        try:
            erase = []
            # Traiter liste_stats (indépendante des alertes popup/mail/telegram)
            for key, value in list(var.liste_stats.items()):
                int_value = int(value)
                
                if int_value == int(var.nbrHs):
                    # Déconnexion détectée
                    if key not in self._stats_recorded_disconnects:
                        meta = self._get_host_metadata(key)
                        hostname = meta['nom'] if meta['nom'] != "Inconnu" else key
                        site = meta['site']
                        
                        stats_manager.record_disconnect(key, hostname, site)
                        logger.info(f"[STATS] Déconnexion enregistrée: {key} [site: {site or 'N/A'}]")
                        
                        # Notification "Système" pour l'historique (sans popup utilisateur)
                        self.notification_manager.add_notification(
                            type_alert='system',
                            message=f"Hôte hors ligne : {hostname} ({key})",
                            level='warning',
                            details={'ip': key, 'nom': hostname, 'site': site}
                        )
                        
                        self._stats_recorded_disconnects.add(key)
                    # Passer à l'état "alerté" pour permettre la détection de reconnexion
                    var.liste_stats[key] = var.STATE_ALERT_SENT
                    
                elif int_value == var.STATE_RECOVERY:
                    # Reconnexion détectée
                    if key in self._stats_recorded_disconnects:
                        meta = self._get_host_metadata(key)
                        hostname = meta['nom'] if meta['nom'] != "Inconnu" else key
                        site = meta['site']
                        
                        stats_manager.record_reconnect(key, hostname, site)
                        logger.info(f"[STATS] Reconnexion enregistrée: {key} [site: {site or 'N/A'}]")
                        
                        # Notification "Système" pour l'historique
                        self.notification_manager.add_notification(
                            type_alert='system',
                            message=f"Hôte rétabli : {hostname} ({key})",
                            level='success',
                            details={'ip': key, 'nom': hostname, 'site': site}
                        )
                        
                        self._stats_recorded_disconnects.discard(key)
                    # Marquer pour suppression
                    erase.append(key)
                    
                elif int_value == var.STATE_ALERT_SENT:
                    # État alerté - s'assurer qu'on l'a dans le set
                    self._stats_recorded_disconnects.add(key)
            
            # Nettoyer les entrées traitées
            for key in erase:
                var.liste_stats.pop(key, None)
                
        except Exception as e:
            logger.error(f"Erreur process_stats: {e}", exc_info=True)

    def process_popup(self):
        """Traite les alertes popup."""
        try:
            erase = []
            ip_hs = ""
            ip_ok = ""
            
            for key, value in list(var.liste_hs.items()):
                # On ignore les popups pour les hôtes exclus
                is_excluded = key in var.liste_exclu

                if int(value) == int(var.nbrHs):
                    if not is_excluded:
                        ip_hs += f"{key}\n "
                    var.liste_hs[key] = var.STATE_ALERT_SENT
                elif int(value) == var.STATE_RECOVERY:
                    if not is_excluded:
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
            erase = []
            hosts_down = []
            hosts_up = []
            
            # Log de diagnostic pour voir l'état des listes
            if var.liste_mail:
                logger.debug(f"[MAIL] État liste_mail: {dict(var.liste_mail)}")
            
            # Vérification préventive de la configuration SMTP
            try:
                smtp_params = db.lire_param_mail()
                # [email, password, port, server, recipients, telegram]
                if not smtp_params or not smtp_params[0] or not smtp_params[3] or not smtp_params[4]:
                    if var.liste_mail:
                        logger.warning("[MAIL] Configuration SMTP incomplète ou manquante - Les alertes mail ne pourront pas être envoyées")
            except Exception as e_smtp:
                logger.error(f"[MAIL] Erreur vérification config SMTP: {e_smtp}")

            for key, value in list(var.liste_mail.items()):
                if key in var.liste_exclu:
                    continue
                    
                if int(value) == int(var.nbrHs):
                    # Hôte qui vient de tomber
                    logger.info(f"Alerte mail: {key} HS")
                    
                    meta = self._get_host_metadata(key)
                    
                    host_info = {
                        'ip': key,
                        'nom': meta['nom'],
                        'mac': meta['mac'],
                        'latence': "HS",
                        'site': meta['site']
                    }
                    hosts_down.append(host_info)
                    
                    # Notification Interne
                    self.notification_manager.add_notification(
                        type_alert='mail',
                        message=f"Alerte Mail : {meta['nom']} ({key}) est HS",
                        level='error',
                        details=host_info
                    )
                    
                    var.liste_mail[key] = var.STATE_ALERT_SENT
                    
                elif int(value) == var.STATE_RECOVERY:
                    # Hôte qui revient en ligne
                    logger.info(f"[MAIL] Alerte retour détectée: {key} revient en ligne")
                    
                    meta = self._get_host_metadata(key)
                    
                    host_info = {
                        'ip': key,
                        'nom': meta['nom'],
                        'mac': meta['mac'],
                        'latence': meta['latence'],
                        'site': meta['site']
                    }
                    hosts_up.append(host_info)
                    
                    # Notification Interne
                    self.notification_manager.add_notification(
                        type_alert='mail',
                        message=f"Rétablissement Mail : {meta['nom']} ({key}) est OK",
                        level='success',
                        details=host_info
                    )
                    
                    erase.append(key)
            
            for cle in erase:
                var.liste_mail.pop(cle, None)
            
            # Envoyer UN SEUL mail groupé si des alertes existent
            if hosts_down or hosts_up:
                logger.info(f"[MAIL] Envoi d'un mail groupé: {len(hosts_down)} HS, {len(hosts_up)} revenu(s)")
                threading.Thread(
                    target=email_sender.send_grouped_alert_email,
                    args=(hosts_down, hosts_up),
                    daemon=True
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
            
            # Vérification préventive de la configuration Telegram
            try:
                if not getattr(thread_telegram, 'REQUESTS_AVAILABLE', False):
                     logger.warning("[TELEGRAM] Module 'requests' manquant - Impossible d'envoyer des alertes Telegram")
                     
                token, chat_ids = thread_telegram.get_telegram_credentials()
                if not token or not chat_ids:
                    if var.liste_telegram:
                        logger.warning("[TELEGRAM] Token ou Chat ID manquant - Les alertes Telegram ne pourront pas être envoyées")
            except Exception as e_tg:
                logger.error(f"[TELEGRAM] Erreur vérification config: {e_tg}")

            for key, value in list(var.liste_telegram.items()):
                if key in var.liste_exclu:
                    continue

                if int(value) == int(var.nbrHs):
                    logger.info(f"Alerte Telegram: {key} HS")
                    
                    meta = self._get_host_metadata(key)
                    site_prefix = f"[{meta['site']}] " if meta['site'] else ""
                    ip_hs_text += f"{site_prefix}{meta['nom']} : {key}\n"
                    
                    # Notification Interne
                    self.notification_manager.add_notification(
                        type_alert='telegram',
                        message=f"Alerte Telegram : {meta['nom']} ({key}) HS",
                        level='error',
                        details={'ip': key, 'nom': meta['nom'], 'site': meta['site']}
                    )
                    
                    var.liste_telegram[key] = var.STATE_ALERT_SENT
                elif int(value) == var.STATE_RECOVERY:
                    meta = self._get_host_metadata(key)
                    site_prefix = f"[{meta['site']}] " if meta['site'] else ""
                    ip_ok_text += f"{site_prefix}{meta['nom']} : {key}\n"
                    
                    # Notification Interne
                    self.notification_manager.add_notification(
                        type_alert='telegram',
                        message=f"Rétablissement Telegram : {meta['nom']} ({key}) OK",
                        level='success',
                        details={'ip': key, 'nom': meta['nom'], 'site': meta['site']}
                    )
                    
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
                threading.Thread(target=thread_telegram.main, args=(message,), daemon=True).start()
                
        except Exception as e:
            logger.error(f"Erreur process telegram: {e}", exc_info=True)

    def process_temp_alerts(self):
        """Traite les alertes de température élevée en utilisant les données fournies."""
        if not self.get_all_hosts_data_callback:
            return

        try:
            seuil = int(var.tempSeuil)
            hosts_high_temp = []
            hosts_normal_temp = []
            
            # Récupérer toutes les données via le callback
            all_hosts_data = self.get_all_hosts_data_callback()
            
            for host in all_hosts_data:
                ip = host.get('ip')
                if not ip or ip in var.liste_exclu:
                    continue
                
                temp_text = host.get('temp')
                if not temp_text:
                    continue
                
                # Extraire la valeur numérique de la température
                try:
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
                        # Première alerte
                        if var.liste_temp_alert[ip] == 1:
                            nom = host.get('nom') or "Inconnu"
                            hosts_high_temp.append({
                                'ip': ip,
                                'nom': nom,
                                'temp': temp,
                                'seuil': seuil
                            })
                            logger.warning(f"🌡️ Alerte température: {ip} ({nom}) = {temp}°C (seuil: {seuil}°C)")
                            
                            # Notification Interne
                            self.notification_manager.add_notification(
                                type_alert='temperature',
                                message=f"Température élevée : {nom} ({ip}) - {temp}°C",
                                level='warning',
                                details={'ip': ip, 'nom': nom, 'temp': temp, 'seuil': seuil}
                            )
                            
                            var.liste_temp_alert[ip] = var.STATE_ALERT_SENT  # Marquer comme alerté
                else:
                    # Température normale
                    if ip in var.liste_temp_alert:
                        if var.liste_temp_alert[ip] == var.STATE_ALERT_SENT:
                            nom = host.get('nom') or "Inconnu"
                            hosts_normal_temp.append({
                                'ip': ip,
                                'nom': nom,
                                'temp': temp
                            })
                            logger.info(f"🌡️ Température normalisée: {ip} ({nom}) = {temp}°C")
                            
                            # Notification Interne
                            self.notification_manager.add_notification(
                                type_alert='temperature',
                                message=f"Température normale : {nom} ({ip}) - {temp}°C",
                                level='success',
                                details={'ip': ip, 'nom': nom, 'temp': temp}
                            )
                            
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
                    for host in hosts:
                        host_info = {
                            'ip': host['ip'],
                            'nom': host['nom'],
                            'temp': host['temp'],
                            'seuil': host.get('seuil', var.tempSeuil)
                        }
                        threading.Thread(
                            target=email_sender.send_temp_alert_email,
                            args=(host_info, alert_type),
                            daemon=True
                        ).start()
                except Exception as e:
                    logger.error(f"Erreur envoi email température: {e}")
            
            # Telegram
            if var.telegram:
                full_message = self.main_window.tr("Alerte sur le site ") + var.nom_site + "\n\n" + message
                threading.Thread(target=thread_telegram.main, args=(full_message,), daemon=True).start()
                
        except Exception as e:
            logger.error(f"Erreur envoi alertes température: {e}", exc_info=True)
