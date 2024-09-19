from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex

import logging

logger = logging.getLogger(__name__)

class VMListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vms = []

    def update_data(self, vm_list):
        self.beginResetModel()
        self.vms = vm_list
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self.vms)

    def data(self, index, role):

        if not index.isValid():
            return None
        if index.row() >= len(self.vms):
            return None

        vm = self.vms[index.row()]
        if role == Qt.DisplayRole:
            return vm.name
        elif role == Qt.UserRole:
            return vm
        elif role == Qt.UserRole + 1:
            return vm.icon_path
        elif role == Qt.UserRole + 2:
            return vm.running
        elif role == Qt.UserRole + 3:
            return vm.vmid

        return None

