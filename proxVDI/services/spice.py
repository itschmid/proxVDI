from PyQt5.QtCore import QProcess, QObject
from configparser import ConfigParser
from urllib.parse import urlparse, urlunparse
import tempfile
import logging

logger = logging.getLogger(__name__)

class Spice(QObject):

    def __init__(self, parent=None):
        super(Spice, self).__init__(parent)
        self.config = None
        self.node = None

    def set_config(self, node, config):
        self.config = config
        self.node = node

    def replace_hostname_in_url(self, url, new_ip):
        parsed_url = urlparse(url)
        new_netloc = f"{new_ip}:{parsed_url.port}" if parsed_url.port else new_ip
        new_url = parsed_url._replace(netloc=new_netloc)
        return urlunparse(new_url)

    def create_temp_config_file(self, config):
        cfg = ConfigParser()
        cfg['virt-viewer'] = config

        original_url = cfg['virt-viewer'].get('proxy')
        if not original_url or not self.node:
            logger.error("Original URL or node IP missing, cannot update URL.")
            return None

        new_ip = self.node['ip']
        updated_url = self.replace_hostname_in_url(original_url, new_ip)
        cfg['virt-viewer']['proxy'] = updated_url

        try:
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.ini') as temp_file:
                cfg.write(temp_file)
                return temp_file.name
        except Exception as e:
            logger.error(f"Failed to create or write to temp file: {e}")
            return None

    def start_spice(self):
        if not self.config:
            logger.error("Configuration not set.")
            return False

        temp_file = self.create_temp_config_file(self.config)
        if not temp_file:
            logger.error("Failed to create configuration file.")
            return False

        cmd = "remote-viewer"
        proc = QProcess(self)
        success = proc.startDetached(cmd, [temp_file])
        if success:
            logger.info("SPICE viewer started successfully.")
        else:
            logger.error("Failed to start SPICE viewer.")
        return success
