## Copyright Dynag ##
## https://prog.dynag.co ##
## thread_lancement.py ##

import threading
import time
from src import thread_mail, thread_recap_mail, thread_telegram, var, db

# Thread des alertes #
## Lancement des alertes ##
def main(self, model):
    mailRecap(self, model)
    while True:
        time.sleep(10)
        if int(var.delais) < 10:
            time.sleep(10)
        else:
            time.sleep(int(var.delais))

        try:
            if var.tourne is True:
                if var.popup is True:
                    try:
                        threading.Thread(target=popup, args=(self,)).start()
                    except Exception as inst:
                        print("popup "+inst)
                if var.mail is True:
                    try:
                        threading.Thread(target=mail, args=(self, model,)).start()
                    except Exception as inst:
                        print(inst)
                if var.telegram is True:
                    try:
                        threading.Thread(target=telegram, args=(self, model,)).start()
                    except Exception as inst:
                        print(inst)
            else:
                break
        except Exception as inst:
            print(inst)

## Mail recap ##
def mailRecap(self, model):
    print("lancement")
    if var.tourne is True:
        print("tourne OK")
        if var.mailRecap is True:
            try:
                threading.Thread(target=thread_recap_mail.main, args=(self, model,)).start()
            except Exception as inst:
                print(inst)

## Popup ##
def popup(self):
    try:
        time.sleep(0)
        erase = ()
        ip_hs = ""
        ip_ok = ""
        for key, value in var.liste_hs.items():
            if int(value) == int(var.nbrHs):
                ip_hs = ip_hs + key + "\n "
                var.liste_hs[key] = 10
            elif value == 20:
                ip_ok = ip_ok + key + "\n "
                erase = erase + (str(key),)
        for cle in erase:
            try:
                del var.liste_hs[cle]
            except:
                pass
        if len(ip_hs) > 0:
            mess = self.tr("les hotes suivants sont HS : \n") + ip_hs
            #threading.Thread(target=showinfo("alerte", mess)).start()
            self.popup_signal.emit(mess)
        if len(ip_ok) > 0:
            mess = self.tr("les hotes suivants sont OK : \n") + ip_ok
            self.popup_signal.emit(mess)
        ip_hs = ""
        ip_ok = ""
    except Exception as inst:
        print(inst)

## Alertes mail ##
def mail(self, model):
    # time.sleep(10)
    try:
        erase = ()
        ip_hs1 = ""
        ip_ok1 = ""
        mess = 0
        message = self.tr("""\
                Bonjour,<br><br>
                <table border=1><tr><td width='50%' align=center>Nom</td><td width='50%' align=center>IP</td></tr>
                """)
        sujet = "Allerte sur le site " + var.nom_site
        time.sleep(1)
        for key1, value1 in var.liste_mail.items():
            if int(value1) == int(var.nbrHs):
                nom = db.lireNom(key1, model)
                p1 = "<tr><td align=center>" + nom + "</td><td bgcolor=" + var.couleur_noir + " align=center>" + key1 + "</td></tr>"
                ip_hs1 = ip_hs1 + p1
                var.liste_mail[key1] = 10

            elif value1 == 20:
                nom = db.lireNom(key1, model)
                p1 = "<tr><td align=center>" + nom + "</td><td bgcolor=" + var.couleur_vert + " align=center>" + key1 + "</td></tr>"
                ip_ok1 = ip_ok1 + p1
                erase = erase + (str(key1),)
        for cle in erase:
            try:
                del var.liste_mail[cle]
            except Exception as inst:
                print("fct_thread--" + str(inst))
        if len(ip_hs1) > 0:
            mess = 1
            message = message + self.tr("""\
                        Les hôtes suivants sont <font color=red>HS</font><br>""") + ip_hs1 + self.tr("""\
                        </table><br><br>
                        Cordialement,
                        """)

        if len(ip_ok1) > 0:
            mess = 1
            message = message + self.tr("""\
                        Les hôtes suivants sont <font color=green>revenus</font><br>""") + ip_ok1 + self.tr("""\
                        </table><br><br>
                        Cordialement,
                         """)
        print("mail preparé")
        if mess == 1:

            threading.Thread(target=thread_mail.envoie_mail, args=(message, sujet)).start()
            mess = 0
    except Exception as inst:
       print("fct_thread--" + str(inst))

## Alertes Télégram ##
def telegram(self, model):
    try:
        erase = ()
        ip_hs1 = ""
        ip_ok1 = ""
        mess = 0
        message = self.tr("Alerte sur le site ") + var.nom_site + "\n \n"
        time.sleep(1)
        for key1, value1 in var.liste_telegram.items():
            if int(value1) == int(var.nbrHs):
                nom = db.lireNom(key1, model)
                p1 = "" + nom + " : " + key1 + "\n"
                ip_hs1 = ip_hs1 + p1
                var.liste_telegram[key1] = 10

            elif value1 == 20:
                nom = db.lireNom(key1, model)
                p1 = "" + nom + " : " + key1 + "\n"
                ip_ok1 = ip_ok1 + p1
                erase = erase + (str(key1),)
        for cle in erase:
            try:
                del var.liste_telegram[cle]
            except:
                pass

        if len(ip_hs1) > 0:
            mess = 1
            message = message + self.tr("les hotes suivants sont HS : \n") + ip_hs1

        if len(ip_ok1) > 0:
            mess = 1
            message = message + self.tr("les hotes suivants sont OK : \n") + ip_ok1
        if mess == 1:
            threading.Thread(target=thread_telegram.main, args=(message,)).start()
            mess = 0
    except Exception as inst:
        print("fct_thread--" + str(inst))

## Recap mail ##
def recapmail(self, model):
    print("lancement recap")
    thread_recap_mail.main(self, model)
