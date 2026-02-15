# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import src.ip_fct as fct_ip
from src import var
import threading
import multiprocessing
import queue




################s###########################################################################
#####   Fonction principale d'ajout de ip.pin   				    				  #####
###########################################################################################

def labThread(value):
    var.progress['value'] = value


def worker(q, comm):
    while True:
        task = q.get()
        if task is None:
            q.task_done()
            break
        
        # Déballer les arguments
        # args expected: (self, comm, model, ip, tout, i, hote, port, site)
        try:
            threadIp(task[0], task[1], task[2], task[3], task[4], task[5], task[6], task[7], task[8])
        except Exception as e:
            print(f"Erreur thread worker: {e}")
        finally:
            q.task_done()

try:
    from src.utils.http_checker import check_website_sync
except ImportError:
    check_website_sync = None

def threadIp(self, comm, model, ip, tout, i, hote, port, site=""):
    # Vérifie si l'IP existe déjà dans le modèle
    ipexist = False
    # Note: Accès concurrent au modèle Qt peut être risqué, idéalement utiliser des signaux ou verrous
    # Ici on suppose que model.rowCount() et model.item() sont safe en lecture ou gérés par Qt
    # (En général, QStandardItemModel n'est pas thread-safe pour les écritures, mais lecture ça peut aller si pas de modif concurrente)
    
    # Optimisation: évitons de parcourir le modèle si possible ou faisons le dans le thread principal avant
    # Pour l'instant on garde la logique existante
    
    # Utilisation de méthodes thread-safe via invokeMethod ou similaire serait mieux, 
    # mais gardons la structure actuelle en espérant que le modèle n'est pas modifié ailleurs
    
    try:
        for row in range(model.rowCount()):
            item = model.item(row, 1)
            if item and item.text() == ip:
                # Affiche une alerte (à adapter selon ton système)
                print(f"L'adresse {ip} existe déjà")
                ipexist = True
                break
    except Exception:
        pass # Risque de race condition ignoré pour l'instant

    if not ipexist:
        # Simule le ping et la récupération des infos
        
        # Détection URL
        is_url = ip.startswith('http://') or ip.startswith('https://')
        
        if is_url and check_website_sync:
             # Utiliser le checker HTTP
             res = check_website_sync(ip, timeout=5)
             result = "OK" if res['success'] else "HS"
        else:
             # Ping classique
             result = fct_ip.ipPing(ip)  # "OK" ou autre
        nom = ""
        mac = ""
        port_val = port
        extra = site  # Le site est passé via extra
        is_ok = (result == "OK")
        
        # Normaliser le type de scan (accepter français et anglais de l'API web)
        tout_lower = str(tout).lower()
        is_all = (tout == self.tr("Tout") or tout_lower == "all")
        is_site_mode = (tout == self.tr("Site") or tout_lower == "site")
        
        if is_all:
            # Mode "Tous" : Ajoute TOUS les hôtes (UP et DOWN)
            if is_ok:
                try:
                    nom = fct_ip.socket.gethostbyaddr(ip)[0]
                except Exception:
                    # Fallback SNMP
                    snmp_name = fct_ip.resolve_snmp_name(ip, timeout=0.5)
                    nom = snmp_name if snmp_name else ip
                try:
                    mac = fct_ip.getmac(ip)
                except Exception:
                    mac = ""
                if port:
                    port_val = fct_ip.check_port(ip, port)
            else:
                # Hôte DOWN : Mettre au moins l'IP comme nom
                nom = ip
                port_val = ""
                mac = ""
                # Ajouter à la liste des hôtes HS pour le récapitulatif
                var.scan_hs_hosts.append(ip)
            # Ajoute la ligne via le signal (UP ou DOWN) avec le site
            comm.addRow.emit(i, ip, nom, mac, str(port_val), site, is_ok)
            var.u += 1
        elif is_site_mode:
            # Mode "Site" : Ajoute sans ping avec le site
            comm.addRow.emit(i, ip, ip, "", "", site, False)
            var.u += 1
        else:
            # Mode "Alive" : Ajoute UNIQUEMENT les hôtes UP
            if is_ok:
                try:
                    nom = fct_ip.socket.gethostbyaddr(ip)[0]
                except Exception:
                    # Fallback SNMP
                    snmp_name = fct_ip.resolve_snmp_name(ip, timeout=0.5)
                    nom = snmp_name if snmp_name else ip
                try:
                    mac = fct_ip.getmac(ip)
                except Exception:
                    mac = ""
                port_val = fct_ip.check_port(ip, port)
                comm.addRow.emit(i, ip, nom, mac, str(port_val), site, True)
                var.u += 1
            else:
                # Hôte DOWN
                pass
                
    var.thread_ferme += 1
    # Eviter division par zéro
    if var.thread_ouvert > 0:
        thread_tot = ((var.thread_ouvert - (var.thread_ouvert - var.thread_ferme)) / var.thread_ouvert) * 100
        comm.progress.emit(int(thread_tot))


###########################################################################################
#####   Préparation de l'ajout      												  #####
###########################################################################################
def main(self, comm, model, ip, hote, tout, port, mac, site=""):
    nbrworker = min(32, multiprocessing.cpu_count() * 4) # Limiter à une valeur raisonnable
    q = queue.Queue()
    threads = []
    
    # Calculer le nombre total de tâches à l'avance pour la progress bar globalement
    # Ce n'est pas parfait car on ne sait pas encore exactement combien d'IPs on va scanner
    # Mais le code original utilisait 'hote' comme nombre total attendu
    var.thread_ouvert = int(hote)
    var.thread_ferme = 0
    
    # Démarrer les workers
    for i in range(nbrworker):
        t = threading.Thread(target=worker, args=(q, comm), daemon=True)
        t.start()
        threads.append(t)

    # Importer le parser d'URL pour gérer les ports
    is_url = False
    if tout != self.tr("Site"):
        try:
            from src.utils.url_parser import parse_host_port
            parsed = parse_host_port(ip)
            is_url = (ip.startswith('http://') or ip.startswith('https://') or 
                      parsed['has_port'] or any(c.isalpha() for c in parsed['host']))
        except ImportError:
            is_url = (ip.startswith('http://') or ip.startswith('https://') or 
                      any(c.isalpha() for c in ip))
    
    if is_url:
        # Mode URL/Site
        print(f"URL/Site web détecté: {ip}")
        q.put((self, comm, model, ip, tout, 0, 1, port, site))
        
    else:
        # Mode IP classique
        if not ip or ip.count('.') != 3:
            print(f"Erreur: IP invalide '{ip}' - abandon du scan")
            # Arrêter les workers proprement
            for _ in range(nbrworker): q.put(None)
            return

        ip1 = ip.split(".")
        try:
            for part in ip1: int(part)
        except ValueError:
            print(f"Erreur: IP invalide '{ip}'")
            for _ in range(nbrworker): q.put(None)
            return

        i = 0
        u = 0
        hote_count = int(hote)
        
        while i < hote_count:
            ip2 = ip1[0] + "." + ip1[1] + "."
            ip3 = int(ip1[3]) + i

            if int(ip3) <= 255:
                ip2 = ip2 + ip1[2] + "." + str(ip3)
            else:
                ip4 = int(ip1[2]) + 1
                ip2 = ip2 + str(ip4) + "." + str(u)
                u = u + 1
            
            # Enqueue task
            q.put((self, comm, model, ip2, tout, i, hote, port, site))
            i += 1

    # Attendre que toutes les tâches soient traitées
    q.join()

    # Arrêter les workers
    for _ in range(nbrworker):
        q.put(None)
    for t in threads:
        t.join()

    # Scan terminé - émettre la notification via le serveur web si disponible
    if hasattr(self, 'web_server') and self.web_server:
        self.web_server.emit_scan_complete(var.u)

