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
        
        # Connecter le signal popup local au signal de la fenêtre principale
        self.popup_signal.connect(self.main_window.show_popup)

    def start(self):
        """Démarre la surveillance des alertes."""
        logger.info(f"Démarrage du gestionnaire d'alertes avec nbrHs={var.nbrHs} (alertes après {var.nbrHs} pings échoués)")
        self.check_mail_recap()
        
        # Démarrer le timer avec le délai configuré
        delay_ms = max(10, int(var.delais)) * 1000
        self.timer.start(delay_ms)

    def stop(self):
        """Arrête la surveillance."""
        self.timer.stop()
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
        except Exception as e:
            logger.error(f"Erreur vérification alertes: {e}", exc_info=True)

    def check_mail_recap(self):
        """Lance le thread de récapitulatif mail."""
        if var.tourne and var.mailRecap:
            try:
                threading.Thread(target=thread_recap_mail.main, args=(self.main_window, self.model)).start()
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
                elif value == 20:
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
            
            # Log de diagnostic pour voir l'état des compteurs
            if var.liste_mail:
                logger.debug(f"[ALERTE] Vérification alertes mail - nbrHs={var.nbrHs}, compteurs: {dict(var.liste_mail)}")
            
            for key, value in list(var.liste_mail.items()):
                if int(value) == int(var.nbrHs):
                    # Hôte qui vient de tomber - LOG IMPORTANT
                    logger.info(f"[ALERTE] Déclenchement alerte pour {key}: compteur={value} atteint seuil nbrHs={var.nbrHs}")
                    nom = db.lireNom(key, self.model) or "Inconnu"
                    
                    # Récupérer les infos de l'hôte depuis le modèle
                    mac = ""
                    latence = "HS"
                    for row in range(self.model.rowCount()):
                        item_ip = self.model.item(row, 1)
                        if item_ip and item_ip.text() == key:
                            mac_item = self.model.item(row, 3)
                            mac = mac_item.text() if mac_item else ""
                            break
                    
                    host_info = {
                        'ip': key,
                        'nom': nom,
                        'mac': mac,
                        'latence': latence
                    }
                    hosts_down.append(host_info)
                    var.liste_mail[key] = 10
                    
                elif value == 20:
                    # Hôte qui revient en ligne
                    nom = db.lireNom(key, self.model) or "Inconnu"
                    
                    # Récupérer les infos de l'hôte
                    mac = ""
                    latence = "OK"
                    for row in range(self.model.rowCount()):
                        item_ip = self.model.item(row, 1)
                        if item_ip and item_ip.text() == key:
                            mac_item = self.model.item(row, 3)
                            latence_item = self.model.item(row, 5)
                            mac = mac_item.text() if mac_item else ""
                            latence = latence_item.text() if latence_item else "OK"
                            break
                    
                    host_info = {
                        'ip': key,
                        'nom': nom,
                        'mac': mac,
                        'latence': latence
                    }
                    hosts_up.append(host_info)
                    erase.append(key)
            
            for cle in erase:
                var.liste_mail.pop(cle, None)
            
            # Envoyer les alertes avec les nouveaux templates
            for host_down in hosts_down:
                threading.Thread(
                    target=email_sender.send_alert_email,
                    args=(host_down, 'down')
                ).start()
            
            for host_up in hosts_up:
                threading.Thread(
                    target=email_sender.send_alert_email,
                    args=(host_up, 'up')
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
            
            # Log de diagnostic
            if var.liste_telegram:
                logger.debug(f"[ALERTE] Vérification alertes telegram - nbrHs={var.nbrHs}, compteurs: {dict(var.liste_telegram)}")
            
            for key, value in list(var.liste_telegram.items()):
                if int(value) == int(var.nbrHs):
                    logger.info(f"[ALERTE TELEGRAM] Déclenchement pour {key}: compteur={value} atteint seuil nbrHs={var.nbrHs}")
                    nom = db.lireNom(key, self.model) or "Inconnu"
                    ip_hs_text += f"{nom} : {key}\n"
                    var.liste_telegram[key] = 10
                elif value == 20:
                    nom = db.lireNom(key, self.model) or "Inconnu"
                    ip_ok_text += f"{nom} : {key}\n"
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
