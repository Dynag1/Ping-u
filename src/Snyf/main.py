from PySide6.QtWidgets import QDialog
import threading
from src.Snyf import send

version = "0.1.0"
print("main")
def main(self, comm):
    from src.Snyf.ui_fen import Ui_Dialog
    dialog = QDialog()
    sfenetre = Ui_Dialog()
    sfenetre.setupUi(dialog)

    def valider(comm, dialog):
        threads = []
        if sfenetre.checkHik.isChecked():
            t = threading.Thread(target=send.send, args=("hik", comm, dialog))
            t.start()
            threads.append(t)
        """if sfenetre.checkAxis.isChecked():
            t = threading.Thread(target=send.send, args=("axis", comm, dialog))
            t.start()
            threads.append(t)"""
        if sfenetre.checkOnvif.isChecked():
            t = threading.Thread(target=send.send, args=("onvif", comm, dialog))
            t.start()
            threads.append(t)
        if sfenetre.checkAvigilon.isChecked():
            t = threading.Thread(target=send.send, args=("avigilon", comm, dialog))
            t.start()
            threads.append(t)
        if sfenetre.checkSamsung.isChecked():
            t = threading.Thread(target=send.send, args=("samsung", comm, dialog))
            t.start()
            threads.append(t)
        if sfenetre.checkUpnp.isChecked():
            t = threading.Thread(target=send.send, args=("upnp", comm, dialog))
            t.start()
            threads.append(t)
        dialog.reject()  # Ferme correctement la fenêtre

    sfenetre.labTitre.setText("Snyf, récupération automatique des éléments.\n Version " + version)
    sfenetre.pushAnnule.clicked.connect(dialog.reject)
    sfenetre.pushValid.clicked.connect(lambda: valider(comm, dialog))
    dialog.exec()
