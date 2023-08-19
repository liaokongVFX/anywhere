from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtSvg

from anywhere.utils import RESOURCES_PATH


def show_message(message, message_type='success', parent=None):
    if message_type == 'success':
        return QtWidgets.QMessageBox.information(parent, '提示', message)
    return QtWidgets.QMessageBox.critical(parent, '提示', message)


def show_question(question, parent=None):
    response = QtWidgets.QMessageBox.question(parent, '询问', question)
    return response == QtWidgets.QMessageBox.Yes


class SignalBus(QtCore.QObject):
    """ 全局事件总线 """

    history_item_changed = QtCore.Signal(dict)
    config_saved = QtCore.Signal()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(SignalBus, cls).__new__(cls, *args, **kwargs)

        return cls._instance


signal_bus = SignalBus()


def create_h_spacer_item():
    return QtWidgets.QSpacerItem(
        0, 0, QtWidgets.QSizePolicy.Expanding,
        QtWidgets.QSizePolicy.Minimum)


def create_v_spacer_item():
    return QtWidgets.QSpacerItem(
        0, 0, QtWidgets.QSizePolicy.Minimum,
        QtWidgets.QSizePolicy.Expanding)


def svg_to_pixmap(svg_name, width, height, color):
    svg_path = f'{RESOURCES_PATH}/images/{svg_name}'
    renderer = QtSvg.QSvgRenderer(svg_path)
    pixmap = QtGui.QPixmap(width, height)
    pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(
        painter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QtGui.QColor(color))
    painter.end()
    return pixmap


class Message(QtWidgets.QWidget):
    closed = QtCore.Signal()

    def __init__(self, text, msg_type='info', duration=None, closable=False, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Dialog |
            QtCore.Qt.WA_TranslucentBackground |
            QtCore.Qt.WA_DeleteOnClose
        )
        self.setAttribute(QtCore.Qt.WA_StyledBackground)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    label = QtWidgets.QLabel()
    pixmap = svg_to_pixmap('success_fill.svg', 32, 32, '#FF0000')
    label.setPixmap(pixmap)
    label.show()
    app.exec_()
