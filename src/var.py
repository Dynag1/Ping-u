# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import threading
from src.utils.colors import AppColors

version = "99.03.03"
nom = "Ping ü"
nom_logiciel = "PingU"
site = 'http://prog.dynag.co'

thread_ouvert = 0
thread_ferme = 0
u = 0

tourne = True
delais = 5
nbrHs = 3  # Nombre de tentatives échouées avant d'envoyer une alerte (par défaut: 3)

# Événement pour arrêter proprement les threads (mail recap, etc.)
# Utiliser stop_event.set() pour arrêter et stop_event.clear() pour réinitialiser
stop_event = threading.Event()

popup = False
mail = False
telegram = False
mailRecap = False
dbExterne = False
envoie_alert = False

# Alerte température
tempAlert = False  # Activer/désactiver les alertes température
tempSeuilWarning = 60  # Seuil de warning (visuel uniquement)
tempSeuil = 70         # Seuil critique (visuel + alerte)
liste_temp_alert = {}  # Format: {'ip': compteur}

liste_hs = {}
liste_mail = {}
liste_telegram = {}

# Cache SNMP - Stockage global des données de trafic réseau et des débits calculés
# Format: {'ip': {'in': octets, 'out': octets, 'timestamp': float}}
traffic_cache = {}
# Format: {'ip': {'in_mbps': float, 'out_mbps': float}}
bandwidth_cache = {}

couleur_vert = AppColors.VERT_PALE
couleur_jaune = AppColors.JAUNE_PALE
couleur_orange = AppColors.ORANGE_PALE
couleur_rouge = AppColors.ROUGE_PALE
couleur_noir = AppColors.NOIR_GRIS

bg_frame_haut = AppColors.BG_FRAME_HAUT
bg_frame_mid = AppColors.BG_FRAME_MID
bg_frame_droit = AppColors.BG_FRAME_DROIT
bg_but = AppColors.BG_BUT

# Gestion multi-sites
sites_list = ["Site 1"]  # Liste des sites disponibles
sites_actifs = []  # Sites à surveiller (vide = tous)
site_filter = []  # Sites à afficher (vide = tous)