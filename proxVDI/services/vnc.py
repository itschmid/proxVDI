from PyQt5.QtCore import QProcess, QObject
from configparser import ConfigParser

import tempfile
import os

class VncClient(QObject):

    def __init__(self, parent=None):
        super(VncClient, self).__init__(parent)
        self.config = None
        self.node = None

    def set_config(self, node, config):
        self.config = config
        self.node = node

    def create_temp_config_file(self, config):
        cfg = ConfigParser()
        virtviewer = {
            'host': config['host'],
            'type': "vnc",
            'port': config['port'],
            'user': config['user'],
            'password': config['ticket']
        }
        print(virtviewer)
        cfg['virt-viewer'] = virtviewer

        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.ini') as temp_file:
                cfg.write(temp_file)
                temp_file_path = temp_file.name
        except Exception as e:
            print(f"Error creating temp file: {e}")

        return temp_file_path

    def start_vnc(self):
        if not self.config:
            print("Configuration not set.")
            return False

        temp_file_path = self.create_temp_config_file(self.config)
        if not temp_file_path:
            print("Failed to create configuration file.")
            return False

        cmd = "remote-viewer"
        proc = QProcess(self)
        success = proc.startDetached(cmd, [temp_file_path])
        if success:
            print("VNC started successfully.")
        else:
            print("Failed to start VNC.")
        return success


