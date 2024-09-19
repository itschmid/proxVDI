import proxmoxer.core
from PyQt5.QtCore import pyqtSignal, QObject, QThread, pyqtSignal, QMetaObject

from ..services.spice import Spice
from ..services.vnc import VncClient

import logging

logger = logging.getLogger(__name__)

class ProxmoxController(QObject):
    data_ready = pyqtSignal(list)
    signal_auth_okay = pyqtSignal()
    signal_auth_failed = pyqtSignal(str)

    def __init__(self, proxmox, parent=None):
        super().__init__()
        self.proxmox = proxmox
        self.host = parent.server

    def get_details_from_vm(self, vmid):
        pass
    def open_spice_client(self, vm_item):

        if vm_item.running:
            spiceconfig = self.proxmox.nodes(vm_item.node).qemu(vm_item.vmid).spiceproxy.post()
            nodes = self.proxmox.cluster.status.get()
            node = next((node for node in nodes if node['name'] == vm_item.node), None)
            print(node)
            spice = Spice(self)
            spice.set_config(node, spiceconfig)
            spice.start_spice()

    def open_vnc_client(self, vm_item):
        if vm_item.running:

            vncconfig = self.proxmox.nodes(vm_item.node).qemu(vm_item.vmid).vncproxy.post()
            vncconfig['host'] = self.host
            nodes = self.proxmox.cluster.status.get()
            node = next((node for node in nodes if node['name'] == vm_item.node), None)
            print(node['ip'])
            print(vncconfig)
            vnc = VncClient(self)
            vnc.set_config(node, vncconfig)
            vnc.start_vnc()

    def start_vm(self, vm_item):
        logger.info("Starting VM...")
        try:
            if not vm_item.running:
                if vm_item.type == "qemu":
                    self.proxmox.nodes(vm_item.node).qemu(vm_item.vmid).status.start.post(timeout=30)
                else:
                    pass
        except proxmoxer.core.ResourceException as e:
            logger.error(str(e))

    def shutdown_vm(self, vm_item):
        logger.info("Shutdown VM...")
        try:
            if vm_item.running:
                if vm_item.type == "qemu":
                    self.proxmox.nodes(vm_item.node).qemu(vm_item.vmid).status.shutdown.post(timeout=30)
                else:
                    pass
        except proxmoxer.core.ResourceException as e:
            logger.error(str(e))
    def stop_vm(self, vm_item):
        logger.info("Stopping VM...")
        try:
            if vm_item.running:
                if vm_item.type == "qemu":
                    self.proxmox.nodes(vm_item.node).qemu(vm_item.vmid).status.stop.post(timeout=30)
                else:
                    pass
        except proxmoxer.core.ResourceException as e:
            logger.error(str(e))

    def reboot_vm(self, vm_item):
        logger.info("Reboot VM...")
        try:
            if vm_item.running:
                if vm_item.type == "qemu":
                    self.proxmox.nodes(vm_item.node).qemu(vm_item.vmid).status.reboot.post(timeout=30)
                else:
                    pass
        except proxmoxer.core.ResourceException as e:
            logger.error(str(e))
