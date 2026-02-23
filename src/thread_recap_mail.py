# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import time
from datetime import datetime
from src import var, thread_mail, db
from src.utils.logger import get_logger

logger = get_logger(__name__)


def jour_demande():
    jourDemande = tuple()
    try:
        data = db.lire_param_mail_recap()
        if not data or len(data) < 8:
            return jourDemande
        if data[1]:
            jourDemande = jourDemande + ("0",)
        if data[2]:
            jourDemande = jourDemande + ("1",)
        if data[3]:
            jourDemande = jourDemande + ("2",)
        if data[4]:
            jourDemande = jourDemande + ("3",)
        if data[5]:
            jourDemande = jourDemande + ("4",)
        if data[6]:
            jourDemande = jourDemande + ("5",)
        if data[7]:
            jourDemande = jourDemande + ("6",)
    except Exception as e:
        logger.error(f"Erreur jour_demande: {e}")
    return jourDemande


def prepaMail(self, get_hosts_callback, test_mode=False):
    """Prépare et envoie l'email récapitulatif avec template HTML moderne."""
    try:
        from src import email_sender
        
        # Collecter les données des hôtes
        hosts_data = []
        hosts = get_hosts_callback() if get_hosts_callback else []
        for host in hosts:
            nom = host.get('nom') or "Inconnu"
            ip = host.get('ip') or "N/A"
            statut_text = host.get('latence') or "N/A"
            temp_text = host.get('temp') or ""
            
            # Déterminer le statut
            status = 'offline' if statut_text == "HS" else 'online'
            
            # Extraire la valeur numérique de la température si présente
            temp_value = None
            if temp_text:
                try:
                    # Enlever le °C si présent et convertir en float
                    temp_clean = temp_text.replace('°C', '').replace('°', '').strip()
                    if temp_clean:
                        temp_value = float(temp_clean)
                except (ValueError, AttributeError):
                    pass
            
            hosts_data.append({
                'ip': ip,
                'nom': nom,
                'status': status,
                'latence': statut_text,
                'temp': temp_text,
                'temp_value': temp_value
            })
        
        # Trier les hôtes: HS en premier, puis ceux avec température, puis les autres
        def sort_key(host):
            # Priorité 0 = HS (en premier)
            # Priorité 1 = avec température
            # Priorité 2 = en ligne sans température
            if host['status'] == 'offline':
                return (0, host['nom'].lower())
            elif host['temp_value'] is not None:
                return (1, host['nom'].lower())
            else:
                return (2, host['nom'].lower())
        
        hosts_data.sort(key=sort_key)
        
        # Envoyer l'email avec le nouveau template
        email_sender.send_recap_email(hosts_data, test_mode=test_mode)
        
    except Exception as inst:
        logger.error(f"Erreur prepaMail: {inst}", exc_info=True)


def main(self, get_hosts_callback):
    while True:
        try:
            # Vérifier l'arrêt demandé via stop_event ou var.tourne
            if var.stop_event.is_set() or not var.tourne:
                logger.info("Mail recap: arrêt demandé")
                break
                
            if var.mailRecap:
                try:
                    data = db.lire_param_mail_recap()
                    heureDemande = data[0].strftime("%H:%M") if data and data[0] else "00:00"
                except Exception as e:
                    logger.error(f"Erreur lecture config mail recap dans le thread: {e}")
                    heureDemande = "00:00"
                    
                a = False
                j = jour_demande()
                d = datetime.now()
                jour = str(d.weekday())
                heure = d.strftime('%H:%M')
                for x in j:
                    if str(x) == jour:
                        if str(heure) == str(heureDemande):
                            a = True
                if a is True:
                    prepaMail(self, get_hosts_callback)
                
                # Utiliser stop_event.wait() au lieu de time.sleep()
                # Cela permet d'interrompre immédiatement quand stop_event.set() est appelé
                if var.stop_event.wait(timeout=60):
                    logger.info("Mail recap: arrêt signalé via stop_event")
                    break
            else:
                break
        except Exception as inst:
            logger.error("thread_recap - " + str(inst), exc_info=True)
