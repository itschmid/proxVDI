import importlib.resources

from PyQt5 import uic
import sys
import logging, os
from PyQt5.QtCore import pyqtSignal, QSettings
from PyQt5.QtGui import QPixmap

logger = logging.getLogger(__name__)

p = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(p)

LoginBase, LoginForm = uic.loadUiType(p + "/ui/login.ui")

class Login(LoginBase, LoginForm):
    signal_login = pyqtSignal(str, str, str)
    signal_message = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        logger.info("------------ login ------------------")
        self.setupUi(self)
        self.parent = parent

        self.settings = QSettings('IT-Schmid', 'ProxVDI')
        self.loadSettings()

        with importlib.resources.path('proxVDI.logo', 'proxvdi_logo_small.png') as icon_path:
            self.logo.setPixmap(QPixmap(str(icon_path)))
        self.logo.setScaledContents(True)

    def loadSettings(self):
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
        logger.info("get authentication information and emit signal to login")
        user = self.username_field.text()
        realm = self.realmList.currentText()
        password = self.password_field.text()
        server = self.nodeList.currentText()
        username = f"{user}@{realm}"

        if not username == '' and not password == '':
            logger.info("authentication")
            self.signal_login.emit(server, username, password)
        else:
            logger.info("empty")
            self.signal_message.emit(1, "username or password is empty")

    def set_message(self, msg):
        self.msg_label.setText(msg)

    def clear_form(self):
        self.username_field.clear()
        self.password_field.clear()






