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

def worker(q, thread_no):
    try:
        while True:
            item = q.get()
            if item is None:
                break
            q.task_done()
    except Exception as e:
        print(e)
        #design.logs("fct_ping - " + str(e))


def threadIp(self, comm, model, ip, tout, i, hote, port):
    # Vérifie si l'IP existe déjà dans le modèle
    ipexist = False
    for row in range(model.rowCount()):
        item = model.item(row, 1)
        if item and item.text() == ip:
            # Affiche une alerte (à adapter selon ton système)
            print(f"L'adresse {ip} existe déjà")
            ipexist = True
            break

    if not ipexist:
        # Simule le ping et la récupération des infos
        result = fct_ip.ipPing(ip)  # "OK" ou autre
        nom = ""
        mac = ""
        port_val = port
        extra = ""
        is_ok = (result == "OK")
        
        # Normaliser le type de scan (accepter français et anglais de l'API web)
        tout_lower = str(tout).lower()
        is_all = (tout == self.tr("Tout") or tout_lower == "all")
        is_site = (tout == self.tr("Site") or tout_lower == "site")
        
        if is_all:
            # Mode "Tous" : Ajoute TOUS les hôtes (UP et DOWN)
            if is_ok:
                try:
                    nom = fct_ip.socket.gethostbyaddr(ip)[0]
                except Exception:
                    nom = ip
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
            # Ajoute la ligne via le signal (UP ou DOWN)
            comm.addRow.emit(i, ip, nom, mac, str(port_val), extra, is_ok)
            var.u += 1
        elif is_site:
            # Mode "Site" : Ajoute sans ping
            comm.addRow.emit(i, ip, ip, "", "", "", False)
            var.u += 1
        else:
            # Mode "Alive" : Ajoute UNIQUEMENT les hôtes UP
            if is_ok:
                try:
                    nom = fct_ip.socket.gethostbyaddr(ip)[0]
                except Exception:
                    nom = ip
                try:
                    mac = fct_ip.getmac(ip)
                except Exception:
                    mac = ""
                port_val = fct_ip.check_port(ip, port)
                comm.addRow.emit(i, ip, nom, mac, str(port_val), extra, True)
                var.u += 1
    var.thread_ferme += 1
    thread_tot = ((var.thread_ouvert - (var.thread_ouvert - var.thread_ferme)) / var.thread_ouvert) *100
    comm.progress.emit(thread_tot)



###########################################################################################
#####   Préparation de l'ajout      												  #####
###########################################################################################
def main(self, comm, model,ip, hote, tout, port, mac):
    nbrworker = multiprocessing.cpu_count()
    num_worker_threads = nbrworker
    q = queue.Queue()
    threads = []
    var.thread_ouvert = int(hote)
    var.thread_ferme = 0
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker, args=(q, i,), daemon=True)
        t.start()
        threads.append(t)
    """
    for parent in var.app_instance.tab_ip.get_children():
        result = var.app_instance.tab_ip.item(parent)["values"]
        ip1 = result[0]
        q.put(ip1)
    """
    # block until all tasks are done
    q.join()
    # stop workers
    for i in range(num_worker_threads):
        q.put(None)
    for t in threads:
        t.join()
    if tout != self.tr("Site"):
        ip1 = ip.split(".")
        u = 0
        i = 0
        if int(hote) > 500:
            # Émettre la fin du scan via le serveur web si disponible
            if hasattr(self, 'web_server') and self.web_server:
                self.web_server.emit_scan_complete(hote)
            return
        while i < int(hote):
            ip2 = ip1[0] + "." + ip1[1] + "."
            ip3 = int(ip1[3]) + i

            i = i + 1
            if int(ip3) <= 255:
                ip2 = ip2 + ip1[2] + "." + str(ip3)
            else:
                ip4 = int(ip1[2]) + 1
                ip2 = ip2 + str(ip4) + "." + str(u)
                u = u + 1
            t = i
            q.put(threading.Thread(target=threadIp, args=(self, comm, model,ip2, tout, i, hote, port)).start())
        
        # Scan terminé - émettre la notification
        if hasattr(self, 'web_server') and self.web_server:
            self.web_server.emit_scan_complete(hote)
    else:
        ip2=ip
        q.put(threading.Thread(target=threadIp, args=(self, comm, model,ip2, tout, i, hote, port)).start())
        
        # Scan terminé - émettre la notification
        if hasattr(self, 'web_server') and self.web_server:
            self.web_server.emit_scan_complete(1)
