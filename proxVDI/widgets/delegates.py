from PyQt5.QtWidgets import QItemDelegate
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt, QSize, QRect, QPen
from PyQt5.QtCore import pyqtSignal, QEvent
import logging

logger = logging.getLogger(__name__)

class VMDelegate(QItemDelegate):

    clicked = pyqtSignal(int)

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

    def sizeHint(self, QStyleOptionViewItem, index):
        return QSize(100, 125)

    def paint(self, painter, option, index):
        painter.save()

        vm_item = index.data(Qt.UserRole)
        if not vm_item:
            painter.restore()
            return

        vm_name = index.data(Qt.DisplayRole)
        vm_icon_path = index.data(Qt.UserRole + 1)
        vm_running = index.data(Qt.UserRole + 2)

        # Berechnung der Position für das Icon und den Text
        icon_size = QSize(64, 64)
        icon_x = option.rect.center().x() - icon_size.width() // 2
        icon_y = option.rect.top() + 10  # Etwas Abstand vom oberen Rand
        text_y = icon_y + icon_size.height() + 5  # Abstand zum Icon

        # Rahmen für das Icon
        frame_rect = QRect(icon_x - 5, icon_y - 5, icon_size.width() + 10, icon_size.height() + 10)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawRoundedRect(frame_rect, 10, 10)

        # Icon zeichnen
        icon = QIcon(vm_icon_path)
        pixmap = icon.pixmap(icon_size)
        painter.drawPixmap(QRect(icon_x, icon_y, icon_size.width(), icon_size.height()), pixmap)

        if vm_running:
            painter.setBrush(Qt.green)
        else:
            painter.setBrush(Qt.red)

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        status_point_size = 10
        status_point_x = icon_x + icon_size.width() - status_point_size // 2
        status_point_y = icon_y + icon_size.height() - status_point_size // 2
        painter.drawEllipse(status_point_x, status_point_y, status_point_size, status_point_size)

        # Text zeichnen
        text_rect = QRect(option.rect.left() + 5, text_y, option.rect.width() - 10, 50)

        if index == self.main_window.selected_index:
            painter.fillRect(text_rect, Qt.blue)  # Füllt nur den Textbereich
            painter.setPen(Qt.white)  # Weißer Text
        else:
            painter.setPen(Qt.black)

        painter.drawText(text_rect, Qt.AlignCenter | Qt.TextWordWrap, vm_name)
        painter.restore()

    def editorEvent(self, event, model, option, index):

        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            logger.debug("SingleClick")
            item = model.data(index, Qt.UserRole)
            item.selected = not item.selected
            model.dataChanged.emit(index, index)
            return True

        elif event.type() == QEvent.MouseButtonDblClick and event.button() == Qt.LeftButton:
            logger.debug("DoubleClick")
            vm_id = index.data(Qt.UserRole + 3)
            self.clicked.emit(vm_id)
            return True
        return False