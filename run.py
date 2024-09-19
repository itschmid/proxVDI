import logging
import sys

from PyQt5.QtWidgets import QApplication

from proxVDI.main import VDIClient

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(process)d] [%(filename)-16s]:[%(lineno)d] %(message)s',
                        datefmt='%d-%m-%Y:%H:%M:%S'
                        )
    logger = logging.getLogger(__name__)


    app = QApplication(sys.argv)
    window = VDIClient()
    window.show()
    sys.exit(app.exec_())