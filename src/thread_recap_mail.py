# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import time
from datetime import datetime
from src import var, thread_mail, db


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
        print(f"Erreur jour_demande: {e}")
    return jourDemande


def prepaMail(self, tree_model):
    """Prépare et envoie l'email récapitulatif avec template HTML moderne."""
    try:
        from src import email_sender
        
        # Collecter les données des hôtes
        hosts_data = []
        for row in range(tree_model.rowCount()):
            index_nom = tree_model.index(row, 2)  # Colonne Nom
            index_ip = tree_model.index(row, 1)   # Colonne IP
            index_statut = tree_model.index(row, 5)  # Colonne Latence/Statut

            nom = tree_model.data(index_nom) or "Inconnu"
            ip = tree_model.data(index_ip) or "N/A"
            statut_text = tree_model.data(index_statut) or "N/A"
            
            # Déterminer le statut
            status = 'offline' if statut_text == "HS" else 'online'
            
            hosts_data.append({
                'ip': ip,
                'nom': nom,
                'status': status,
                'latence': statut_text
            })
        
        # Envoyer l'email avec le nouveau template
        email_sender.send_recap_email(hosts_data, test_mode=False)
        
    except Exception as inst:
        print(f"Erreur prepaMail: {inst}")
        import traceback
        traceback.print_exc()


def main(self, tree_model):
    try:
        data = db.lire_param_mail_recap()
        if not data or len(data) < 8:
            print("Configuration mail récap non trouvée, thread arrêté")
            return
        heureDemande = data[0].strftime("%H:%M") if data[0] else "00:00"
    except Exception as e:
        print(f"Erreur lecture config mail recap: {e}")
        return
    
    while True:
        try:
            # Vérifier l'arrêt demandé via stop_event ou var.tourne
            if var.stop_event.is_set() or not var.tourne:
                print("Mail recap: arrêt demandé")
                break
                
            if var.mailRecap:
                a = False
                j = jour_demande()
                d = datetime.now()
                jour = str(d.weekday())
                heure = d.strftime('%H:%M')
                for x in j:
                    print(x)
                    if str(x) == jour:
                        if str(heure) == str(heureDemande):
                            a = True
                if a is True:
                    prepaMail(self, tree_model)
                
                # Utiliser stop_event.wait() au lieu de time.sleep()
                # Cela permet d'interrompre immédiatement quand stop_event.set() est appelé
                if var.stop_event.wait(timeout=60):
                    print("Mail recap: arrêt signalé via stop_event")
                    break
            else:
                break
        except Exception as inst:
            print("thread_recap - " + str(inst))
