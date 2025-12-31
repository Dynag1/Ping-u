import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
import os
import src.db as param_mail
import sys

# Import optionnel de GPG (peut échouer dans l'exécutable PyInstaller)
try:
    import gnupg
    import platform
    
    # Désactiver GPG sur Linux car gpg.exe n'existe pas
    if platform.system() == 'Linux':
        raise ImportError("GPG désactivé sur Linux")
    
    gpg_path = os.path.join(os.path.dirname(__file__), "gpg", "gpg.exe")
    gpg = gnupg.GPG(gpgbinary=gpg_path)
    GPG_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"GPG non disponible: {e}")
    gpg = None
    GPG_AVAILABLE = False


def importer_cle_publique(chemin_cle):
    """Importe une clé publique PGP depuis un fichier .asc s'il existe, retourne le fingerprint ou None"""
    if not os.path.exists(chemin_cle):
        print(f"Clé publique absente ({chemin_cle})")
        return None
    with open(chemin_cle, 'r') as f:
        key_data = f.read()
    import_result = gpg.import_keys(key_data)
    print(f"Import de {chemin_cle} :", import_result.results)
    if import_result.fingerprints:
        return import_result.fingerprints[0]
    return None

def chiffrer_message(message, fingerprints):
    """Chiffre le message pour une liste de fingerprints"""
    if not fingerprints:
        return None
    encrypted_data = gpg.encrypt(message, recipients=fingerprints, always_trust=True)
    return str(encrypted_data) if encrypted_data.ok else None

def envoie_mail(messageRecep, sujet):
    try:
        variables = param_mail.lire_param_mail()
        # Ordre correct des paramètres dans la DB (sFenetre.py):
        # [0]=email, [1]=password, [2]=port, [3]=server, [4]=recipients, [5]=telegram_chatid
        destinateur = variables[0]
        password = variables[1]
        port = variables[2]
        smtp_server = variables[3]
        destinataires = [d.strip() for d in variables[4].split(",")]
    except Exception as e:
        print(f"Erreur chargement paramètres mail: {e}")
        import traceback
        traceback.print_exc()
        return False

    dossier_cles = "cle"
    fingerprints = []
    destinataires_chiffres = []
    destinataires_non_chiffres = []

    # 1. Cherche une clé pour chaque destinataire (seulement si GPG est disponible)
    for dest in destinataires:
        if not GPG_AVAILABLE:
            destinataires_non_chiffres.append(dest)
            continue
        nom_cle = f"{dest}.asc"
        chemin_cle = os.path.join(dossier_cles, nom_cle)
        fingerprint = importer_cle_publique(chemin_cle)
        if fingerprint:
            fingerprints.append(fingerprint)
            destinataires_chiffres.append(dest)
        else:
            destinataires_non_chiffres.append(dest)

    # 2. Préparation du message
    message = MIMEMultipart('alternative')
    message['Subject'] = sujet
    message['From'] = destinateur
    message['Date'] = formatdate(localtime=True)

    # 3. Envoi chiffré si possible (seulement si GPG est disponible)
    if GPG_AVAILABLE and fingerprints and len(destinataires_chiffres) > 0:
        message['To'] = ", ".join(destinataires_chiffres)
        message_chiffre = chiffrer_message(messageRecep, fingerprints)
        if message_chiffre:
            message.attach(MIMEText(message_chiffre, "plain"))
            print("Envoi chiffré à :", ", ".join(destinataires_chiffres))
            try:
                # Convertir le port en entier
                port_int = int(port)
                
                # Utiliser SMTP_SSL pour le port 465, SMTP + STARTTLS pour les autres
                if port_int == 465:
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL(smtp_server, port_int, context=context, timeout=10) as server:
                        server.login(destinateur, password)
                        server.sendmail(destinateur, destinataires_chiffres, message.as_string())
                        print("Mail chiffré envoyé avec succès (SSL)")
                else:
                    with smtplib.SMTP(smtp_server, port_int, timeout=10) as server:
                        server.starttls()
                        server.login(destinateur, password)
                        server.sendmail(destinateur, destinataires_chiffres, message.as_string())
                        print("Mail chiffré envoyé avec succès (STARTTLS)")
            except Exception as e:
                print("Erreur d'envoi chiffré :", str(e))
        else:
            print("Erreur lors du chiffrement, envoi en clair à tous.")
            destinataires_non_chiffres.extend(destinataires_chiffres)

    # 4. Envoi en clair pour ceux qui n'ont pas de clé
    if destinataires_non_chiffres:
        try:
            message2 = MIMEMultipart('alternative')
            message2['Subject'] = sujet
            message2['From'] = destinateur
            message2['To'] = ", ".join(destinataires_non_chiffres)
            message2['Date'] = formatdate(localtime=True)
            mimetext_texte = MIMEText(messageRecep, "plain")
            mimetext_html = MIMEText(messageRecep, "html")
            message2.attach(mimetext_texte)
            message2.attach(mimetext_html)
            print("Envoi en clair à :", ", ".join(destinataires_non_chiffres))
            
            # Convertir le port en entier
            port_int = int(port)
            
            # Utiliser SMTP_SSL pour le port 465, SMTP + STARTTLS pour les autres
            if port_int == 465:
                # Port 465 : Connexion SSL directe
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_server, port_int, context=context, timeout=10) as server:
                    server.login(destinateur, password)
                    server.sendmail(destinateur, destinataires_non_chiffres, message2.as_string())
                    print("Mail en clair envoyé avec succès (SSL)")
            else:
                # Port 587 ou autre : STARTTLS
                with smtplib.SMTP(smtp_server, port_int, timeout=10) as server:
                    server.starttls()
                    server.login(destinateur, password)
                    server.sendmail(destinateur, destinataires_non_chiffres, message2.as_string())
                    print("Mail en clair envoyé avec succès (STARTTLS)")
            return True
        except Exception as e:
            print(f"Erreur d'envoi en clair : {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    envoie_mail("Ceci est un message secret envoyé en PGP si possible !", "Message sécurisé")
