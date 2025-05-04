# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import traceback
import os
import urllib3
import xmltodict
from src import var
import requests
import subprocess
from PySide6.QtWidgets import QMessageBox


def getxml():
    try:
        print("maj1")
        url = var.site + "/Pingu/changelog.xml"
        try:
            http = urllib3.PoolManager(
                        cert_reqs='CERT_NONE',
                        timeout=urllib3.Timeout(connect=2.0, read=2.0)
                    )
            response = http.request('GET', url)
            data = xmltodict.parse(response.data)
            print("maj2")
            return data
        except urllib3.exceptions.ReadTimeoutError:
            print("Timeout après 2 secondes")
            return None

    except Exception as e:
        print(f"Failed to parse xml from response: {traceback.format_exc()}")
        return None


def recupDerVer():
    try:
        xml = getxml()
        if xml is None:
            print("Impossible de récupérer les données XML")
            return None

        versions = xml["changelog"]["version"]
        if not versions:
            print("Aucune version trouvée dans le XML")
            return None

        latest_version = versions[0]["versio"]
        print(latest_version)
        return ''.join(latest_version.split('.'))
    except KeyError as e:
        print("Clé manquante dans le XML : "+str(e))
    except Exception as e:
        print("Erreur dans recupDerVer : "+e)
    return None


def download_new_version(version):
    try:
        exe_url = f"{var.site}/Pingu/Ping ü.exe"  # URL du fichier .exe à télécharger
        print(exe_url)
        temp_path = os.path.join(os.getcwd(), "temp.exe")  # Chemin temporaire pour la nouvelle version

        # Télécharger le fichier .exe
        response = requests.get(exe_url, stream=True)
        if response.status_code == 200:
            with open(temp_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Nouvelle version téléchargée : {temp_path}")
            return temp_path  # Retourner le chemin du fichier téléchargé
        else:
            print(f"Erreur lors du téléchargement : {response.status_code}")
            return None
    except Exception as e:
        print(f"Erreur dans download_new_version : {traceback.format_exc()}")
        return None


def launch_updater(new_exe_path):
    try:
        updater_path = os.path.join(os.getcwd(), "updater.exe")
        current_exe = os.path.join(os.getcwd(), "Ping ü.exe")

        # Lancer updater.exe avec les chemins en arguments
        subprocess.Popen([
            updater_path,
            new_exe_path,  # Chemin du .exe téléchargé
            current_exe  # Chemin du .exe à remplacer
        ], shell=False)

        os._exit(0)
    except Exception as e:
        print(f"Erreur lancement updater : {traceback.format_exc()}")


def testVersion(self):
    version = recupDerVer()
    if version is None:
        print("Unable to retrieve the latest version")
        return

    current_version = ''.join(var.version.split('.'))

    if int(current_version) < int(version):
        print("nouvelle version")
        boite = QMessageBox(self)
        boite.setWindowTitle("Mise à jou")
        boite.setText(self.tr('Une mise à jour vers la version ')+version+self.tr(' est disponible. \n Voulez vous la télécharger ?'))

        # Configuration des boutons
        boite.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        boite.setDefaultButton(QMessageBox.No)

        # Définition de l'icône
        boite.setIcon(QMessageBox.Question)

        # Affichage et récupération du résultat
        reponse = boite.exec()
        if reponse == QMessageBox.Yes:
            new_exe_path = download_new_version(version)
            if new_exe_path:
                launch_updater(new_exe_path)


def main(self):
    try:
        testVersion(self)
    except Exception as e:
        print(f"Error in main: {e}")
