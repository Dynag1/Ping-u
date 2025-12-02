import traceback
import os
import urllib3
import xmltodict
from src import var
import webbrowser
from datetime import datetime

try:
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QMessageBox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    class QCoreApplication: pass
    class QMessageBox:
        @staticmethod
        def question(*args): return QMessageBox.No
        @staticmethod
        def information(*args): pass
        @staticmethod
        def warning(*args): pass
        Yes = 1
        No = 0

LOG_FILE = "logs/update.log"

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
        data = xmltodict.parse(response.data)
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

def testVersion(self):
    if not GUI_AVAILABLE:
        # En mode headless, on log juste mais pas de popup
        log("Test de version ignoré en mode headless")
        return

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
            self.tr('Mise à jour'),
            self.tr('Une mise à jour vers la version ') + latest_version + self.tr(" est disponible. \nVoulez-vous ouvrir la page de téléchargement ?"),
            QMessageBox.Yes | QMessageBox.No
        )
        if reponse == QMessageBox.Yes:
            log("L'utilisateur a accepté la mise à jour.")
            # Ouvre la page de téléchargement dans le navigateur
            download_url = f"{var.site}/Pingu/Pingu_Setup.exe"
            webbrowser.open(download_url)
            log(f"Lien de téléchargement ouvert : {download_url}")
            QMessageBox.information(self, self.tr("Mise à jour"), self.tr("La page de téléchargement a été ouverte dans votre navigateur."))
        else:
            log("L'utilisateur a refusé la mise à jour.")
    else:
        log("Aucune mise à jour nécessaire.")
        QMessageBox.warning(None, self.tr("Mise à jour"), self.tr("Votre logiciel est à jour"))

def main(self):
    try:
        testVersion(self)
    except Exception as e:
        log(f"Error in main: {e}")
