import threading
import time
from copy import deepcopy
from datetime import datetime
import json
import os
from src.utils.logger import get_logger

logger = get_logger(__name__)

class NotificationManager:
    """
    Gère l'historique des notifications pour l'interface web.
    Stocke les notifications en mémoire et (optionnellement) sur disque.
    Thread-safe.
    """
    _instance = None
    _lock = threading.RLock()
    
    LIMIT = 1000  # Nombre max de notifications à conserver
    STORAGE_FILE = "bd/notifications.json"

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(NotificationManager, cls).__new__(cls)
                    cls._instance.notifications = []
                    cls._instance.data_lock = threading.RLock()
                    cls._instance._load_notifications()
        return cls._instance

    def add_notification(self, type_alert, message, level="info", details=None):
        """
        Ajoute une notification à l'historique.
        :param type_alert: Type d'alerte (ex: 'mail', 'telegram', 'sound', 'system')
        :param message: Message court
        :param level: Niveau ('info', 'warning', 'error', 'success')
        :param details: Détails supplémentaires (dict)
        """
        with self.data_lock:
            notif = {
                'id': int(time.time() * 1000),
                'timestamp': datetime.now().isoformat(),
                'type': type_alert,
                'message': message,
                'level': level,
                'details': details or {},
                'read': False
            }
            
            self.notifications.insert(0, notif)
            
            # Limiter la taille
            if len(self.notifications) > self.LIMIT:
                self.notifications = self.notifications[:self.LIMIT]
            
            self._save_notifications()
            return notif

    def get_notifications(self, limit=50, unread_only=False):
        """Récupère les notifications récentes."""
        with self.data_lock:
            if unread_only:
                filtered = [n for n in self.notifications if not n['read']]
                return deepcopy(filtered[:limit])
            return deepcopy(self.notifications[:limit])

    def mark_as_read(self, notif_id=None):
        """Marque une ou toutes les notifications comme lues."""
        with self.data_lock:
            count = 0
            for n in self.notifications:
                if notif_id is None or n['id'] == notif_id:
                    if not n['read']:
                        n['read'] = True
                        count += 1
            if count > 0:
                self._save_notifications()
            return count

    def clear_notifications(self):
        """Efface tout l'historique."""
        with self.data_lock:
            self.notifications = []
            self._save_notifications()

    def _load_notifications(self):
        """Charge l'historique depuis le disque."""
        try:
            if os.path.exists(self.STORAGE_FILE):
                with open(self.STORAGE_FILE, 'r', encoding='utf-8') as f:
                    self.notifications = json.load(f)
        except Exception as e:
            logger.error(f"Erreur chargement notifications: {e}")
            self.notifications = []

    def _save_notifications(self):
        """Sauvegarde l'historique sur disque (async ou debounced idéalement, ici simple)."""
        try:
            os.makedirs(os.path.dirname(self.STORAGE_FILE), exist_ok=True)
            with open(self.STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.notifications, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde notifications: {e}")
