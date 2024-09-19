from PyQt5 import uic
import sys
import logging, os
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QInputDialog, QMessageBox

logger = logging.getLogger(__name__)

p = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(p)

SettingsBase, SettingsForm = uic.loadUiType(p + "/ui/settings.ui")

class SettingsGui(SettingsBase, SettingsForm):

    def __init__(self, parent=None):
        super(SettingsGui, self).__init__(parent)
        logger.info("------------ settings ------------------")
        self.setupUi(self)
        self.parent = parent

        self.settings = QSettings('IT-Schmid', 'ProxVDI')
        self.load_settings()

        self.addNodeButton.clicked.connect(self.add_node)
        self.delNodeButton.clicked.connect(self.remove_node)
        self.addRealmButton.clicked.connect(self.add_realm)
        self.delRealmButton.clicked.connect(self.remove_realm)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

    def add_node(self):
        logger.info("Add node")
        node, ok = QInputDialog.getText(self, "Add Node", "Please enter node name or ip")
        if ok and node:
            if self.validate_node(node):
                self.nodeList.addItem(node)
            else:
                QMessageBox.warning(self, "Ungültige IP", "Die eingegebene IP-Adresse ist ungültig.")

    def add_realm(self):
        logger.info("Add Realm")
        realm, ok = QInputDialog.getText(self, "Add Realm", "Please enter realm")
        if ok and realm:
            if self.validate_realm(realm):
                self.realmList.addItem(realm)
            else:
                QMessageBox.warning(self, "Ungültige REALM", "Der eingegebene Realm ist ungültig.")

    def remove_node(self):
        logger.info("Remove node")
        selected_items = self.nodeList.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Keine Auswahl", "Bitte wählen Sie eine IP-Adresse zum Löschen aus.")
            return
        for item in selected_items:
            self.nodeList.takeItem(self.nodeList.row(item))

    def remove_realm(self):
        logger.info("Remove Realm")
        selected_items = self.realmList.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Keine Auswahl", "Bitte wählen Sie eine Realm zum Löschen aus.")
            return
        for item in selected_items:
            self.realmList.takeItem(self.realmList.row(item))

    def validate_node(self, node):
        logger.info("Validate node")
        return True

    def validate_realm(self, node):
        logger.info("Validate realm")
        return True

    def load_settings(self):
        logger.info("Load settings")
        node_list = self.settings.value('node_list', [])
        if node_list:
            for node in node_list:
                self.nodeList.addItem(node)

        realm_list = self.settings.value('realm_list', [])
        if realm_list:
            for realm in realm_list:
                self.realmList.addItem(realm)

    def accept(self):
        logger.info("Accept settings")
        node_list = []
        for index in range(self.nodeList.count()):
            node_list.append(self.nodeList.item(index).text())
        self.settings.setValue('node_list', node_list)

        realm_list = []
        for index in range(self.realmList.count()):
            realm_list.append(self.realmList.item(index).text())
        self.settings.setValue('realm_list', realm_list)

        super().accept()

    def reject(self):
        logger.info("Reject settings")
        super().reject()