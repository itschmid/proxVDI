from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from ..vmmodels import VMItem
from ..const import *
import importlib.resources
import logging

logger = logging.getLogger(__name__)


class Worker(QObject):
    data_ready = pyqtSignal(list)
    load_data = pyqtSignal()

    def __init__(self, proxmox, parent=None):
        super().__init__(parent)
        self.proxmox = proxmox

    def _get_cluster_nodes(self):
        try:
            cluster = self.proxmox.cluster.status.get()
            logger.debug(cluster)
            return cluster
        except Exception as e:
            logger.error(f"Failed to get cluster nodes: {e}")
            return []

    @pyqtSlot()
    def load_vm_data(self):
        logger.info('Loading data from proxmox')
        self.load_data.emit()
        self._get_cluster_nodes()
        self._load_vms()

    def _load_vms(self):
        try:
            vms_data = self.proxmox.cluster.resources.get(type='vm')

        except Exception as e:
            logger.error(f"Error retrieving VM data: {e}")
            vms_data = []

        self.vm_list = []
        for vm_data in vms_data:
            if vm_data.get('template') == 0:  # Verwendung von get() um KeyError zu vermeiden
                processed_vm = self._process_vm_data(vm_data)
                self.vm_list.append(processed_vm)
                print(processed_vm)
        self.data_ready.emit(self.vm_list)

    def _process_vm_data(self, vm_data):
        logger.debug(vm_data)
        if vm_data['type'] == 'qemu':
            config, agent_infos = self._get_vm_config_and_osinfo(vm_data)
            with importlib.resources.path('proxVDI', 'icons') as icons_dir:
                icon_path = self._get_icon_path(config, agent_infos)
                full_icon_path = str(icons_dir / icon_path)
            spice = config.get('vga', {}).startswith("qxl") if "vga" in config else None

            return VMItem(
                name=vm_data['name'],
                icon_path=full_icon_path,
                vmid=vm_data['vmid'],
                node=vm_data['node'],
                status=vm_data['status'],
                type=vm_data['type'],
                os_type=agent_infos.get('result', {}).get('id', None),
                spice=spice,
                running=vm_data['status'] == 'running'
            )

    def _get_vm_config_and_osinfo(self, vm_data):
        try:
            config = self.proxmox.nodes(vm_data['node']).qemu(vm_data['vmid']).config.get()
        except Exception as e:
            logger.error(f"Error retrieving VM config for VMID {vm_data['vmid']}: {e}")
            config = {}

        try:
            agent_infos = self.proxmox(f"nodes/{vm_data['node']}/qemu/{vm_data['vmid']}/agent/get-osinfo").get()
        except Exception as e:
            logger.error(f"Error retrieving OS info for VMID {vm_data['vmid']}: {e}")
            agent_infos = {}

        return config, agent_infos

    def _get_icon_path(self, config, agent_infos):
        os_type = agent_infos.get('result', {}).get('id', None)
        if 'ostype' in config:
            if config['ostype'] in OS_TYPE_LINUX:
                erg =  {
                    'debian': "debian.png",
                    'almalinux': "almalinux.png",
                    'centos': "linux1.png",
                    'fedora': "fedora.png",
                    'redhat': "redhat.png",
                    'suse': "opensuse.png",
                    'opensuse': "opensuse.png",
                }.get(os_type, "linux1.png")

                return erg
            else:
                return "windows.png"
        else:
            return "linux1.png"
