from src import var
from src.fcy_ping import PingManager
from src.core.alert_manager import AlertManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MainController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.ui = main_window.ui
        self.ping_manager = None
        self.alert_manager = None

    def toggle_monitoring(self):
        """Gère le démarrage et l'arrêt du monitoring (Ping + Alertes)."""
        if self.ui.butStart.isChecked():
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        """Démarre tous les services de monitoring."""
        try:
            logger.info(f"Démarrage monitoring (délai: {var.delais}s, seuil HS: {var.nbrHs})")
            
            # Sécurité : Vérifier si le monitoring est déjà en cours
            if self.ping_manager is not None or var.tourne:
                self.stop_monitoring()
                try:
                    from PySide6.QtCore import QThread
                    QThread.msleep(500)
                except ImportError:
                    import time
                    time.sleep(0.5)
            
            # Réinitialiser le stop_event pour permettre aux nouveaux threads de fonctionner
            var.stop_event.clear()
            
            # Réinitialiser les listes d'alertes
            var.liste_hs.clear()
            var.liste_mail.clear()
            var.liste_telegram.clear()
            var.liste_temp_alert.clear()
            
            # Instanciation des managers
            # Note: PingManager prend le modèle de données + main_window pour broadcast
            self.ping_manager = PingManager(self.main_window.treeIpModel, self.main_window)
            self.alert_manager = AlertManager(self.main_window, self.main_window.treeIpModel)
            
            var.tourne = True
            self.ping_manager.start()
            self.alert_manager.start()
            
            # Mise à jour UI - bloquer les signaux pour éviter les triggers en cascade
            self.ui.butStart.blockSignals(True)
            self.ui.butStart.setChecked(True)
            self.ui.butStart.blockSignals(False)
            self.ui.butStart.setStyleSheet(f"background-color: {var.couleur_rouge}; color: black;")
            self.ui.butStart.setText("Stop")
            
        except Exception as e:
            logger.error(f"Erreur démarrage monitoring: {e}", exc_info=True)
            # En cas d'erreur, on remet l'état visuel à l'arrêt
            self.ui.butStart.blockSignals(True)
            self.ui.butStart.setChecked(False)
            self.ui.butStart.blockSignals(False)
            self.stop_monitoring()

    def stop_monitoring(self):
        """Arrête tous les services de monitoring."""
        try:
            logger.info("Arrêt du monitoring via MainController")
            
            # 1. Signaler l'arrêt à tous les threads via stop_event (AVANT de mettre tourne à False)
            # Cela permet aux threads utilisant stop_event.wait() de s'arrêter immédiatement
            var.stop_event.set()
            var.tourne = False
            
            # 2. Arrêter d'abord l'alert manager (qui gère aussi le thread mail recap)
            if self.alert_manager:
                self.alert_manager.stop()
                self.alert_manager = None
            
            # 3. Puis arrêter le ping manager (plus complexe, avec QThread)
            if self.ping_manager:
                self.ping_manager.stop()
                # Traiter les événements Qt en attente pour laisser le temps au thread de se terminer
                try:
                    from PySide6.QtCore import QCoreApplication
                    QCoreApplication.processEvents()
                except ImportError:
                    pass
                self.ping_manager = None
            
            logger.info("Tous les services de monitoring arrêtés")
                
            # Mise à jour UI
            # On vérifie si l'UI existe encore (cas de fermeture)
            if hasattr(self.ui, 'butStart'):
                # Bloquer les signaux pour éviter les triggers en cascade
                self.ui.butStart.blockSignals(True)
                self.ui.butStart.setChecked(False)
                self.ui.butStart.blockSignals(False)
                self.ui.butStart.setStyleSheet(f"background-color: {var.couleur_vert}; color: black;")
                self.ui.butStart.setText("Start")
                    
        except Exception as e:
            logger.error(f"Erreur arrêt monitoring: {e}", exc_info=True)
