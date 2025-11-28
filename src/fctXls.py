# This Python file uses the following encoding: utf-8

import src.var as var
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QFileDialog, QMessageBox
from openpyxl import Workbook
from openpyxl import load_workbook
import os
name = ""


def chSave(self):
    filename, _ = QFileDialog.getSaveFileName(
        parent=self,
        caption=self.tr("Enregistrer le fichier"),
        dir=os.getcwd() + os.sep + "bd",
        filter=self.tr("Fichiers XLS (*.xlsx);;Tous fichiers (*.*)")
    )

    if not filename:
        return

    if not filename:
        return
    return filename


def chOpen(self):
    filename, _ = QFileDialog.getOpenFileName(
        parent=self,
        caption=self.tr("Ouvrir un fichier"),
        dir=os.getcwd() + os.sep + "bd",
        filter=self.tr("Fichiers xlsx (*.xlsx);;Tous fichiers (*.*)")
    )

    if not filename:
        return
    return filename


def saveExcel(self, tree_model):
    try:
        name = chSave(self)  # À remplacer par ta méthode de sélection de fichier

        # Créer le classeur Excel
        workbook = Workbook()
        sheet = workbook.active
        # Entêtes
        headers = [self.tr("IP"), self.tr("Nom"), self.tr("Mac"), self.tr("Port"), self.tr("Latence"), self.tr("Comm")]
        sheet.append(headers)
        # Parcourir le modèle
        for row in range(tree_model.rowCount()):
            # Récupérer les index des colonnes
            ip_index = tree_model.index(row, 1)
            nom_index = tree_model.index(row, 2)
            mac_index = tree_model.index(row, 3)
            port_index = tree_model.index(row, 4)
            latence_index = tree_model.index(row, 5)
            comm_index = tree_model.index(row, 7)
            # Récupérer les données
            ip = ip_index.data()
            nom = nom_index.data()
            mac = mac_index.data()
            port = port_index.data()
            latence = latence_index.data()
            comm = comm_index.data()

            # Écrire dans Excel
            sheet.append([
                str(ip) if ip else "",
                str(nom) if nom else "",
                str(mac) if mac else "",
                str(port) if port else "",
                str(latence) if latence else "",
                str(comm) if comm else ""
            ])

        workbook.save(filename=f"{name}")
        QMessageBox.information(
            self,
            self.tr("Succès"),
            self.tr("Données sauvegardés"),
            QMessageBox.Ok
        )
    except Exception as e:
        print(e)

def openExcel(self, tree_model):
    filename = chOpen(self)
    tree_model.removeRows(0, tree_model.rowCount())

    # Charger le workbook
    try:
        workbook = load_workbook(filename=filename)
        sheet = workbook.active

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            ip = str(row[0]) if row[0] else ""
            nom = str(row[1]) if row[1] else ip
            mac = str(row[2]) if row[2] else ""
            port = str(row[3]) if row[3] else ""
            latence = ""
            comm = str(row[5]) if len(row) > 5 and row[5] else ""

            # Vérifier si l'IP existe déjà
            ip_exists = False
            for i in range(tree_model.rowCount()):
                existing_ip = tree_model.index(i, 0).data()
                if existing_ip == ip:
                    QMessageBox.warning(self, self.tr("Doublon"), f"{self.tr('L\'adresse existe déjà')} : {ip}")
                    ip_exists = True
                    break

            if not ip_exists:
                # Ajouter au modèle
                parent = QModelIndex()  # Racine
                tree_model.insertRow(tree_model.rowCount(parent), parent)
                new_row = tree_model.rowCount(parent) - 1

                tree_model.setData(tree_model.index(new_row, 1, parent), ip)
                tree_model.setData(tree_model.index(new_row, 2, parent), nom)
                tree_model.setData(tree_model.index(new_row, 3, parent), mac)
                tree_model.setData(tree_model.index(new_row, 4, parent), port)
                tree_model.setData(tree_model.index(new_row, 5, parent), latence)
                tree_model.setData(tree_model.index(new_row, 7, parent), comm)
        QMessageBox.information(
            self,
            self.tr("Succès"),
            self.tr("Données importés"),
            QMessageBox.Ok
        )
    except Exception as e:
        QMessageBox.critical(self, self.tr("Erreur"), f"{self.tr('Erreur lors de la lecture')} : {str(e)}")
