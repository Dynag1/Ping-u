# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import socket
import csv
import os
import sys

from src.utils.logger import get_logger
logger = get_logger(__name__)

# Imports conditionnels pour éviter les erreurs en headless
try:
    from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget
    from PySide6.QtCore import QAbstractItemModel, QModelIndex
    from PySide6.QtGui import QStandardItem, QStandardItemModel
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    # Classes factices pour le typage et l'exécution headless
    class QFileDialog: 
        @staticmethod
        def getSaveFileName(*args, **kwargs): return (None, None)
        @staticmethod
        def getOpenFileName(*args, **kwargs): return (None, None)
    class QMessageBox:
        @staticmethod
        def information(*args): pass
        @staticmethod
        def critical(*args): pass
        Ok = 1
    class QAbstractItemModel: pass
    class QModelIndex: pass
    class QStandardItem:
        def __init__(self, text=""): 
            self._text = str(text) if text else ""
            self._data = {}
        def text(self): return self._text
        def setText(self, text): self._text = str(text)
        def setData(self, data, role=0): self._data[role] = data
        def data(self, role=0): return self._data.get(role)
    class QStandardItemModel:
        def __init__(self):
            self._rows = []
            self._headers = []
            self._column_count = 0
        def rowCount(self): return len(self._rows)
        def columnCount(self): return self._column_count
        def appendRow(self, items): 
            self._rows.append(items)
            if len(items) > self._column_count:
                self._column_count = len(items)
        def removeRows(self, row, count): 
            del self._rows[row:row+count]
        def setHorizontalHeaderLabels(self, labels):
            class HeaderItem:
                def __init__(self, text): self._text = str(text)
                def text(self): return self._text
            self._headers = [HeaderItem(l) for l in labels]
            self._column_count = len(labels)
        def horizontalHeaderItem(self, col):
            if 0 <= col < len(self._headers):
                return self._headers[col]
            class DummyItem:
                def text(self): return ""
            return DummyItem()
        def item(self, row, col):
            if 0 <= row < len(self._rows) and 0 <= col < len(self._rows[row]):
                return self._rows[row][col]
            return None
    class QWidget: pass


def getIp(self):
    """
    Obtient l'adresse IP locale de l'interface réseau active.
    Méthode robuste qui fonctionne sur Windows, Linux, et Debian.
    """
    try:
        # Méthode robuste: créer un socket UDP vers une IP externe
        # Sans vraiment envoyer de données, juste pour que le système
        # sélectionne l'interface réseau appropriée
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # On se "connecte" à 8.8.8.8 (Google DNS) sur le port 80
            # Pas besoin que ce soit accessible, on veut juste l'IP locale
            s.connect(('8.8.8.8', 80))
            IP_addres = s.getsockname()[0]
        except Exception:
            # Fallback si la méthode ci-dessus échoue
            IP_addres = '127.0.0.1'
        finally:
            s.close()
        
        # Extraire le sous-réseau (ex: 192.168.1.X -> 192.168.1.1)
        ip = IP_addres.split(".")
        if len(ip) == 4:
            ipadress = ip[0]+"."+ip[1]+"."+ip[2]+".1"
        else:
            ipadress = "192.168.1.1"  # Valeur par défaut
        
        return ipadress
    except Exception as e:
        logger.error(f"Erreur détection IP: {e}", exc_info=True)
        return "192.168.1.1"  # Valeur par défaut en cas d'erreur


def save_csv(self, treeModel, filepath=None, return_path=False, silent=False):
    try:
        # Récupérer le modèle depuis le QTreeView
        model = treeModel

        # Vérifier que le modèle a les méthodes nécessaires (duck typing pour mode headless)
        if not hasattr(model, 'rowCount') or not hasattr(model, 'item'):
            raise ValueError("Modèle invalide - doit avoir rowCount() et item()")

        # Si pas de fichier spécifié, afficher la boîte de dialogue
        if filepath is None:
            filename, _ = QFileDialog.getSaveFileName(
                parent=self,
                caption=self.tr("Enregistrer le fichier"),
                dir=os.getcwd() + os.sep + "bd",
                filter=self.tr("Fichiers PIN (*.pin);;Tous fichiers (*.*)")
            )

            if not filename:
                return None if return_path else None

            # Forcer l'extension .pin si non précisée
            if not filename.lower().endswith('.pin'):
                filename += '.pin'
        else:
            filename = filepath
            # Assurer que le répertoire existe
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

        row_count = model.rowCount()
        # Utiliser un logger si disponible, sinon print
        try:
            from src.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.info(f"Sauvegarde de {row_count} lignes dans {filename}")
        except:
            print(f"Sauvegarde de {row_count} lignes dans {filename}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as myfile:
            csvwriter = csv.writer(myfile, delimiter=',')

            # Parcourir les lignes du modèle
            for row in range(row_count):
                row_data = []
                for column in range(model.columnCount()):
                    index = model.index(row, column)
                    data = model.data(index)
                    row_data.append(data if data is not None else '')
                
                # Ignorer les lignes vides ou contenant uniquement des champs vides
                if all(str(field).strip() == '' for field in row_data):
                    continue
                    
                csvwriter.writerow(row_data)

        # Si return_path est True, retourner le chemin au lieu d'afficher la boîte de dialogue
        if return_path:
            return filename

        # Lancer l'alerte seulement si pas silent
        if not silent and GUI_AVAILABLE:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                self.tr("Succès"),
                self.tr("Données sauvegardés"),
                QMessageBox.Ok
            )
    except Exception as e:
        # Utiliser un logger si disponible
        try:
            from src.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Erreur sauvegarde CSV: {e}")
        except:
            print("design - " + str(e))
            
        if return_path:
            raise
        return


def load_csv(self, treeModel, filepath=None):
    try:
        # Si pas de fichier spécifié, afficher la boîte de dialogue
        if filepath is None:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption=self.tr("Ouvrir un fichier"),
                dir=os.getcwd() + os.sep + "bd",
                filter=self.tr("Fichiers PIN (*.pin);;Tous fichiers (*.*)")
            )

            if not filename:
                return
        else:
            filename = filepath

        # Sauvegarde des en-têtes existants
        headers = [treeModel.horizontalHeaderItem(i).text()
                  for i in range(treeModel.columnCount())] if treeModel.columnCount() > 0 else []

        with open(filename, 'r', encoding='utf-8') as myfile:
            csvread = csv.reader(myfile, delimiter=',')

            # Réinitialisation propre
            treeModel.removeRows(0, treeModel.rowCount())  # Conserve les en-têtes

            for row in csvread:
                # Ignorer les lignes vides ou contenant uniquement des champs vides
                if not row or all(field.strip() == '' for field in row):
                    continue
                items = [QStandardItem(str(field)) for field in row]
                treeModel.appendRow(items)

            # Réapplication des en-têtes si nécessaire
            if headers and treeModel.columnCount() == 0:
                treeModel.setHorizontalHeaderLabels(headers)

        # Afficher la boîte de dialogue seulement si on a une vraie fenêtre Qt (pas en mode headless)
        if GUI_AVAILABLE and filepath is None and isinstance(self, QWidget):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, self.tr("Succès"), self.tr("Données chargées avec succès"), QMessageBox.Ok)

    except Exception as e:
        # Afficher l'erreur seulement si on a une vraie fenêtre Qt (pas en mode headless)
        if GUI_AVAILABLE and filepath is None and isinstance(self, QWidget):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, self.tr("Erreur"), f"Erreur lors du chargement : {str(e)}", QMessageBox.Ok)
        else:
            # En mode headless ou programmatique, juste lever l'exception
            raise



def clear(self, treeModel):
    treeModel.removeRows(0, treeModel.rowCount())


def ip_exists_in_model(model, ip):
    """
    Vérifie si une IP existe déjà dans le modèle.
    
    Args:
        model: Le modèle de données (QStandardItemModel ou équivalent)
        ip: L'adresse IP à vérifier
        
    Returns:
        bool: True si l'IP existe déjà, False sinon
    """
    if not ip or ip.strip() == "":
        return False
    
    ip_clean = ip.strip()
    for row in range(model.rowCount()):
        item = model.item(row, 1)  # Colonne 1 = IP
        if item:
            existing_ip = item.text().strip()
            if existing_ip == ip_clean:
                return True
    return False


def get_all_ips_from_model(model):
    """
    Récupère toutes les IPs uniques du modèle.
    
    Args:
        model: Le modèle de données
        
    Returns:
        set: Ensemble des IPs présentes dans le modèle
    """
    ips = set()
    for row in range(model.rowCount()):
        item = model.item(row, 1)  # Colonne 1 = IP
        if item:
            ip_text = item.text().strip()
            if ip_text:
                ips.add(ip_text)
    return ips


def remove_duplicates_from_model(model):
    """
    Supprime les doublons d'IP du modèle.
    
    Args:
        model: Le modèle de données
        
    Returns:
        int: Nombre de doublons supprimés
    """
    seen_ips = set()
    rows_to_remove = []
    
    for row in range(model.rowCount()):
        item = model.item(row, 1)  # Colonne 1 = IP
        if item:
            ip_text = item.text().strip()
            if ip_text in seen_ips:
                rows_to_remove.append(row)
            elif ip_text:
                seen_ips.add(ip_text)
    
    # Supprimer les lignes en partant de la fin pour éviter les décalages d'index
    for row in reversed(rows_to_remove):
        model.removeRow(row)
    
    return len(rows_to_remove)


def add_row(self, model, row_data):
    """Ajoute une ligne selon le type de modèle"""
    if isinstance(model, QStandardItemModel):
        # Version pour QStandardItemModel
        items = [QStandardItem(str(field)) for field in row_data]
        model.appendRow(items)

    elif hasattr(model, 'add_data'):
        # Version pour modèle personnalisé
        model.add_data(row_data)

    elif hasattr(model, '_data'):
        # Fallback pour modèle basique
        model._data.append(row_data)
        if hasattr(model, 'dataChanged'):
            top_left = model.index(len(model._data)-1, 0)
            bottom_right = model.index(len(model._data)-1, len(row_data)-1)
            model.dataChanged.emit(top_left, bottom_right)


def plug(self):
    # Chemin du dossier 'fichier' situé à côté du script
    script_principal_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Chemin complet du dossier cible (avec sous-dossier 'plugin')
    dossier_fichier = os.path.join(script_principal_dir, 'fichier', 'plugin')

    # Création récursive des dossiers (ne fait rien s'ils existent déjà)
    os.makedirs(dossier_fichier, exist_ok=True)

    # Lister le contenu (uniquement après création du dossier)
    try:
        elements = os.listdir(dossier_fichier)
    except FileNotFoundError:  # Redondant avec makedirs mais sécurisé
        return []

    # Filtrer les sous-dossiers
    sous_dossiers = [
        nom for nom in elements
        if os.path.isdir(os.path.join(dossier_fichier, nom))
    ]

    return sous_dossiers
