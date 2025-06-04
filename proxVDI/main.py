import sys
import os
from PyQt5.QtWidgets import QApplication, QMenu, QDialog, QMessageBox
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5 import uic
from proxmoxer import ProxmoxAPI

from .controller.controllers import ProxmoxController
from .controller.workers import Worker
from .vmmodels import VMListModel, VMItem
from .widgets import VMDelegate, VDIStatusBar
from .dialogs.login import Login
from .dialogs.settings import SettingsGui

import urllib3
import logging

logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
p = os.path.dirname(os.path.abspath(__file__))
sys.path.append(p)

VDIClientBase, VDIClientForm = uic.loadUiType(p + "/ui/vdi2.ui")

class VDIClient(VDIClientBase, VDIClientForm):
    signal_auth_failed = pyqtSignal(str)

    def __init__(self, parent=None):
        super(VDIClient, self).__init__(parent)
        self.setupUi(self)
        self.initializeComponents()
        self.setupConnections()
        self.open_login_dialog()

    def initializeComponents(self):
        """Initialisiere Komponenten der Anwendung."""
        self.proxmox = None
        self.prox_controller = None
        self.selected_index = None
        self.thread = QThread()
        self.setupStatusBar()
        self.setupModelAndView()

    def setupStatusBar(self):
        """Setze die Statusbar der Anwendung auf."""
        self.statusbar = VDIStatusBar(self)
        self.setStatusBar(self.statusbar)

    def setupModelAndView(self):
        """Initialisiere Model und View für die VM-Liste."""
        self.model = VMListModel(self)

        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.model)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.vm_listview.setModel(self.proxyModel)
        self.vm_listview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.delegate = VMDelegate(self, self.vm_listview)
        self.vm_listview.setItemDelegate(self.delegate)

    def filterItems(self, text):
        self.proxyModel.setFilterWildcard(f"*{text}*")

    def setupConnections(self):
        """Richte Verbindungen (Signals und Slots) ein."""
        self.vm_listview.customContextMenuRequested.connect(self.openMenu)
        #self.logout_button.clicked.connect(self.logout)
        self.actionLogin.triggered.connect(self.open_login_dialog)
        self.actionLogout.triggered.connect(self.logout)
        self.actionSetting.triggered.connect(self.settings)
        self.actionExit.triggered.connect(self.close)
        self.search_line.textChanged.connect(self.filterItems)

    def settings(self):
        self.settings_gui = SettingsGui(self)
        self.settings_gui.exec_()

    def open_login_dialog(self):
        """Öffnet das Login-Fenster für Benutzerauthentifizierung."""
        self.login_gui = Login(self)
        self.login_gui.show()
        self.login_gui.signal_login.connect(self.on_authenticate)
        self.login_gui.signal_message.connect(self.messageBox)

    def logout(self):
        """Logge den Benutzer aus und beende die Anwendung."""
        logger.info("Logout")
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.actionLogin.setEnabled(True)
        self.actionLogout.setEnabled(False)

    def on_authenticate(self, server, username, password):
        """Authentifiziere den Benutzer und starte bei Erfolg die Datenverarbeitung."""
        logger.info(f"SERVER: {server}")
        self.server = server
        try:
            self.proxmox = ProxmoxAPI(server, user=username, password=password, verify_ssl=False)

            self.statusbar.set_nodename(server)
            self.start_data_worker()
        except Exception as e:
            self.signal_auth_failed.emit(str(e))
            logger.error(f"Authentication failed: {e}")
        else:
            self.prox_controller = ProxmoxController(self.proxmox, self)
            self.vm_listview.doubleClicked.connect(self.vm_double_clicked)
            self.reload_button.clicked.connect(self.worker.load_vm_data)
            self.login_gui.close()
            self.actionLogin.setEnabled(False)
            self.actionLogout.setEnabled(True)


    def start_data_worker(self):
        """Startet den Daten-Worker im Hintergrund-Thread."""
        if not self.proxmox or self.thread.isRunning():
            return
        self.worker = Worker(self.proxmox)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.load_vm_data)
        self.worker.data_ready.connect(self.model.update_data)
        self.worker.data_ready.connect(self.statusbar.stop_progress)
        self.worker.load_data.connect(self.statusbar.start_progress)
        self.thread.start()

    def openMenu(self, position):
        """
        Erstellt ein Kontextmenü für die VM-Liste, das verschiedene Aktionen ermöglicht.
        """
        proxy_index = self.vm_listview.indexAt(position)
        if not proxy_index.isValid():
            return

        # Mappe den Proxy-Index auf den Ursprungs-Index im ursprünglichen Modell
        source_index = self.proxyModel.mapToSource(proxy_index)
        if not source_index.isValid():
            return

        vm_item = self.model.vms[source_index.row()]
        menu = QMenu()
        action_map = {
            "Open": lambda: self.handle_vm_action(self.open_vm,vm_item),
            "Start": lambda: self.handle_vm_action(self.prox_controller.start_vm, vm_item, 5000),
            "Shutdown": lambda: self.handle_vm_action(self.prox_controller.shutdown_vm, vm_item, 30000),
            "Stop": lambda: self.handle_vm_action(self.prox_controller.stop_vm, vm_item, 30000),
            "Reboot": lambda: self.prox_controller.reboot_vm(vm_item),
            "Details for VM ID: {0}".format(vm_item.vmid): lambda: self.show_vm_details(vm_item)
        }

        for action_text, func in action_map.items():
            action = menu.addAction(action_text)
            action.triggered.connect(lambda _, f=func: f())

        menu.exec_(self.vm_listview.viewport().mapToGlobal(position))

    def handle_vm_action(self, action_func, vm_item, delay=None):
        """
        Führt eine Aktion für eine VM aus und plant optional das Neuladen der VM-Daten.
        """
        action_func(vm_item)
        if delay:
            QTimer.singleShot(delay, self.worker.load_vm_data)

    def messageBox(self, type, msg):
        if type == 1:
            reply = QMessageBox.information(self, "Info:", msg)
        elif type == 2:
            reply = QMessageBox.warning(self, "Warning", msg)

    def vm_double_clicked(self, index):
        logger.debug("item double clicked")
        vm_item = self.model.vms[index.row()]
        self.open_vm(vm_item)

    def open_vm(self, vm_item):
        logger.info(f"Opening VM {vm_item.vmid}")
        logger.debug(f"{vm_item.type} {vm_item.spice}")
        if vm_item.type == "qemu" and vm_item.spice == True:
            logger.info("QEMU SPICE")
            self.prox_controller.open_spice_client(vm_item)
        elif vm_item.type == "qemu":
            logger.info("QEMU VNC")
            self.prox_controller.open_vnc_client(vm_item)
        elif vm_item.type == "lxc":
            logger.info("LXC VNC")
            self.prox_controller.open_vnc_client(vm_item)

    def show_vm_details(self, vm_item):
        logger.info(f"Node {vm_item.node}")
        logger.info(f"Showing details for VM {vm_item.vmid}")
        x = self.prox_controller.get_details_from_vm(vm_item.vmid)
        logger.info(x)
    def cleanUp(self):
        """Räumt Ressourcen auf, wenn die Anwendung geschlossen wird."""
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()


