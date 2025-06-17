## Copyright Dynag ##
## https://prog.dynag.co ##
## lic.py ##

import os
import pickle
import platform
import uuid
import hashlib
from datetime import datetime


def lire_param_gene():
    fichierini = "tabG"

    try:
        if os.path.isfile(fichierini):
            fichierSauvegarde = open(fichierini,"rb")
            variables = pickle.load(fichierSauvegarde)
            fichierSauvegarde.close()

            #Affichage de la liste
            lic = variables[1]
            return lic

    except Exception as inst:
       print(inst)

def generate_activation_code():
    """Génère un code d'activation unique basé sur la machine de l'utilisateur"""
    machine_info = f"{platform.node()}{uuid.getnode()}{platform.processor()}"
    hashed = hashlib.sha256(machine_info.encode()).hexdigest()
    return f"ACT-{hashed[:16]}-{datetime.now().strftime('%y%m')}"


def jours_restants_licence():
    """Affiche le nombre de jours restants avant expiration de la licence"""
    from datetime import datetime
    license_key = lire_param_gene()

    try:
        if not license_key.startswith("LIC-") or len(license_key) != 45:
            return "Licence invalide"

        expiry_str = license_key.split('-')[1]
        expiry_date = datetime.strptime(expiry_str, "%Y%m%d")
        aujourdhui = datetime.now()

        if aujourdhui > expiry_date:
            return "Licence expirée"

        jours_restants = (expiry_date - aujourdhui).days
        return f"{jours_restants}"

    except Exception as e:
        return f"Erreur de lecture : {str(e)}"

def verify_license():
    """Vérifie si une licence est valide"""
    secret_key = "Sruq_Opiwhjttil_Wtyxzllne"
    activation_code = generate_activation_code()
    license_key = lire_param_gene()
    import hmac
    from datetime import datetime

    try:
        if not license_key.startswith("LIC-") or len(license_key) != 45:
            return False


        expiry_str = license_key.split('-')[1]
        expiry_date = datetime.strptime(expiry_str, "%Y%m%d")
        if datetime.now() > expiry_date:
            return False

        expected_signature = hmac.new(
            secret_key.encode(),
            activation_code.encode(),
            hashlib.sha256
        ).hexdigest()[:32]

        received_signature = license_key.split('-')[2]

        if not hmac.compare_digest(expected_signature, received_signature):
            return False
        else:
            return True

    except Exception as e:
        return False

