## Copyright Dynag ##
## https://prog.dynag.co ##
## thread_maj.py ##

import traceback
import os
import urllib3
import xmltodict
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QMessageBox
from src import var
import requests
import subprocess
from datetime import datetime

LOG_FILE = "update.log"

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {message}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Erreur écriture log : {e}")

def getxml():
    try:
        log("Début récupération du changelog XML")
        url = var.site + "/" + var.nom_logiciel + "/changelog.xml"
        log(f"URL changelog : {url}")
        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        response = http.request('GET', url)
        if response.status != 200:
            log(f"Erreur HTTP : {response.status}")
            return None
        if not response.data or response.data.strip() == b"":
            log("Le fichier XML est vide.")
            return None
        try:
            data = xmltodict.parse(response.data)
        except Exception as e:
            log(f"Erreur parsing XML : {e}\nContenu reçu : {response.data[:200]}")
            return None
        log("Récupération et parsing XML réussis")
        return data
    except Exception:
        log(f"Failed to parse xml from response: {traceback.format_exc()}")
        return None


def recupDerVer(self):
    try:
        log("Recherche de la dernière version disponible...")
        xml = getxml()
        if xml is None:
            log("Impossible de récupérer les données XML")
            return None

        versions = xml["changelog"]["version"]
        if not versions:
            log("Aucune version trouvée dans le XML")
            return None

        latest_version = versions[0]["versio"]
        log(f"Dernière version trouvée : {latest_version}")
        return ''.join(latest_version.split('.')), latest_version
    except KeyError as e:
        log("Clé manquante dans le XML : " + str(e))
    except Exception as e:
        log("Erreur dans recupDerVer : " + str(e))
    return None

def download_new_version(version):
    try:
        exe_url = f"{var.site}/ScryBook/ScryBook.exe"
        temp_path = os.path.join(os.getcwd(), "ScryBook_new.exe")
        log(f"Téléchargement de la nouvelle version depuis {exe_url}...")

        response = requests.get(exe_url, stream=True)
        if response.status_code == 200:
            with open(temp_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            log(f"Nouvelle version téléchargée avec succès : {temp_path}")
            return temp_path
        else:
            log(f"Erreur lors du téléchargement : code HTTP {response.status_code}")
            return None
    except Exception:
        log(f"Erreur dans download_new_version : {traceback.format_exc()}")
        return None

def launch_updater(new_exe_path):
    try:
        updater_path = os.path.join(os.getcwd(), "updater.exe")
        current_exe = os.path.join(os.getcwd(), "ScryBook.exe")
        subprocess.Popen([updater_path, new_exe_path, current_exe], shell=False)
        # Fermer proprement la fenêtre principale AVANT de quitter
        from PySide6.QtWidgets import QApplication
        QApplication.quit()  # Ferme la fenêtre principale
        import sys
        sys.exit(0)
    except Exception:
        log(f"Erreur lancement updater : {traceback.format_exc()}")


def testVersion(self):
    log("Début du test de version")
    result = recupDerVer(self)
    if result is None:
        log("Impossible de récupérer la dernière version")
        return

    version, latest_version = result
    current_version = ''.join(var.version.split('.'))
    log(f"Version installée : {current_version} | Version disponible : {version}")

    if int(current_version) < int(version):
        log(f"Nouvelle version détectée ({latest_version}), demande à l'utilisateur...")
        reponse = QMessageBox.question(
            self,
            QCoreApplication.translate("MainWindow", 'Mise à jour'),
            QCoreApplication.translate("MainWindow", 'Une mise à jour vers la version ') + latest_version + QCoreApplication.translate("MainWindow", " est disponible. \n Voulez vous la télécharger ?"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reponse == QMessageBox.Yes:
            log("L'utilisateur a accepté la mise à jour.")
            new_exe_path = download_new_version(version)
            if new_exe_path:
                launch_updater(new_exe_path)
            else:
                log("Le téléchargement de la nouvelle version a échoué.")
        else:
            log("L'utilisateur a refusé la mise à jour.")
    else:
        log("Aucune mise à jour nécessaire.")
        QMessageBox.warning(None, QCoreApplication.translate("MainWindow", "Mise à jour"), QCoreApplication.translate("MainWindow", "Votre logiciel est à jour"))

def main(self):
    try:
        testVersion(self)
    except Exception as e:
        log(f"Error in main: {e}")

