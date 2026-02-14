import threading
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)

class HostManager:
    """
    Gestionnaire d'état des hôtes thread-safe.
    Sert de source de vérité pour le serveur web, découplé de l'interface Qt.
    """
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(HostManager, cls).__new__(cls)
                    cls._instance.hosts = {} # Dict[id, dict] ou Dict[ip, dict] ? 
                    # Utilisons un dict interne simple, la clé peut être l'IP si unique, ou une ID.
                    # Comme l'app utilise beaucoup l'IP comme clé, essayons de mapper par IP.
                    # Attention les doublons sont possibles dans l'app Qt, mais problématiques pour un dict par IP.
                    # Le serveur web itérait sur les lignes, donc supportait les doublons.
                    # Pour supporter les doublons, utilisons une liste ou un dict par ID de ligne.
                    # Mais l'ID de ligne change si on supprime.
                    # Utilisons l'ID unique (colonne 0) si stable, sinon une liste.
                    cls._instance.hosts = [] 
                    cls._instance.data_lock = threading.RLock()
        return cls._instance

    def clear(self):
        with self.data_lock:
            self.hosts = []

    def set_hosts(self, hosts_list):
        """Remplace toute la liste (pour initialisation ou resync complète)."""
        with self.data_lock:
            self.hosts = deepcopy(hosts_list)

    def update_host_status(self, ip, latency, status, temp=None):
        """Met à jour le statut d'un ou plusieurs hôtes par IP."""
        with self.data_lock:
            for host in self.hosts:
                if host.get('ip') == ip:
                    host['latence'] = latency
                    host['status'] = status
                    if temp:
                        host['temp'] = temp

    def get_all_hosts(self):
        with self.data_lock:
            return deepcopy(self.hosts)

    def get_host_by_ip(self, ip):
        with self.data_lock:
            for host in self.hosts:
                if host.get('ip') == ip:
                    return deepcopy(host)
        return None
