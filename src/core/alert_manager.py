from PySide6.QtCore import QObject, QTimer, Signal
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
        logger.info("Démarrage du gestionnaire d'alertes")
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
            
            for key, value in list(var.liste_mail.items()):
                if int(value) == int(var.nbrHs):
                    # Hôte qui vient de tomber
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
            
            for key, value in list(var.liste_telegram.items()):
                if int(value) == int(var.nbrHs):
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
