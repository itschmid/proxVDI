import sys
from PyQt5.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt5.QtCore import QTimer

import logging

logger = logging.getLogger(__name__)

class VDIStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.node_label = QLabel(f"Node: -")
        self.addWidget(self.node_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMaximumHeight(8)
        self.progress_bar.setTextVisible(False)
        self.addPermanentWidget(self.progress_bar)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress_bar)

    def set_nodename(self, name):
        self.node_label.setText(f"Node: {name}")

    def start_progress(self):
        logger.debug("Start progress bar")
        if not self.timer.isActive():
            self.timer.start(10)

    def stop_progress(self):
        logger.debug("Stop progress bar")
        if self.timer.isActive():
            self.timer.stop()
            self.progress_bar.setValue(0)

    def update_progress_bar(self):
        value = (self.progress_bar.value() + 1) % 100
        self.progress_bar.setValue(value)

