
class VMItem:
    def __init__(self, name, icon_path, vmid, status, node, type, spice=False,os_type=None, running=False, selected=False):
        self.name = name
        self.icon_path = icon_path
        self.vmid = vmid
        self.status = status
        self.running = running
        self.selected = selected
        self.node = node
        self.type = type
        self.spice = spice
        self.os_type = os_type

