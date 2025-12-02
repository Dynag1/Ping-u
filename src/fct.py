# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import socket
import csv
import os
import sys

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
        def __init__(self, text=""): self._text = text
        def text(self): return self._text
    class QStandardItemModel:
        def rowCount(self): return 0
        def columnCount(self): return 0
        def appendRow(self, items): pass
        def removeRows(self, row, count): pass
    class QWidget: pass


def getIp(self):
    try:
        h_name = socket.gethostname()
        IP_addres = socket.gethostbyname(h_name)
        ip = IP_addres.split(".")
        ipadress = ip[0]+"."+ip[1]+"."+ip[2]+".1"
        return ipadress
    except Exception as e:
        print("fct_ip - " + str(e))


def save_csv(self, treeModel, filepath=None, return_path=False, silent=False):
    try:
        # Récupérer le modèle depuis le QTreeView
        model = treeModel

        if not isinstance(model, QAbstractItemModel):
            raise ValueError("Modèle invalide - doit hériter de QAbstractItemModel")

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
                    row_data.append(model.data(index))
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
