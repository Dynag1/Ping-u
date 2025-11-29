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
            logger.info("Démarrage du monitoring via MainController")
            
            # Instanciation des managers
            # Note: PingManager prend le modèle de données, AlertManager aussi
            self.ping_manager = PingManager(self.main_window.treeIpModel)
            self.alert_manager = AlertManager(self.main_window, self.main_window.treeIpModel)
            
            var.tourne = True
            self.ping_manager.start()
            self.alert_manager.start()
            
            # Mise à jour UI
            self.ui.butStart.setStyleSheet(f"background-color: {var.couleur_rouge}; color: black;")
            self.ui.butStart.setText("Stop")
            
        except Exception as e:
            logger.error(f"Erreur démarrage monitoring: {e}", exc_info=True)
            # En cas d'erreur, on remet l'état visuel à l'arrêt
            self.ui.butStart.setChecked(False)
            self.stop_monitoring()

    def stop_monitoring(self):
        """Arrête tous les services de monitoring."""
        try:
            logger.info("Arrêt du monitoring via MainController")
            var.tourne = False
            
            # Arrêter d'abord l'alert manager (plus simple, juste un QTimer)
            if self.alert_manager:
                self.alert_manager.stop()
                self.alert_manager = None
            
            # Puis arrêter le ping manager (plus complexe, avec QThread)
            if self.ping_manager:
                self.ping_manager.stop()
                # Traiter les événements Qt en attente pour laisser le temps au thread de se terminer
                from PySide6.QtCore import QCoreApplication
                QCoreApplication.processEvents()
                self.ping_manager = None
                
            # Mise à jour UI
            # On vérifie si l'UI existe encore (cas de fermeture)
            if hasattr(self.ui, 'butStart'):
                self.ui.butStart.setStyleSheet(f"background-color: {var.couleur_vert}; color: black;")
                self.ui.butStart.setText("Start")
                if self.ui.butStart.isChecked():
                    self.ui.butStart.setChecked(False)
                    
        except Exception as e:
            logger.error(f"Erreur arrêt monitoring: {e}", exc_info=True)
