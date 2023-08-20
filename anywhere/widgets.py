from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtSvg

import qtawesome
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
    message_copied = QtCore.Signal(str)

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

    def __init__(self, text, msg_type='info', duration=1.3, top=32, closable=False, parent=None):
        super().__init__(parent)
        self.top = top

        code_by_type = {
            'info': '#1890ff',
            'success': '#52c41a',
            'warning': '#fadb14',
            'error': '#f5222d'
        }

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Dialog |
            QtCore.Qt.WA_TranslucentBackground |
            QtCore.Qt.WA_DeleteOnClose
        )
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setObjectName('message_object')
        self.setStyleSheet(f'#message_object{{border: 1px solid {code_by_type[msg_type]}}}')

        icon_label = QtWidgets.QLabel()
        icon_label.setPixmap(svg_to_pixmap(f'{msg_type}_fill.svg', 20, 20, code_by_type[msg_type]))

        self.content_label = QtWidgets.QLabel(text)
        self.content_label.setStyleSheet('font-size: 12px')
        self.close_button = QtWidgets.QToolButton()
        self.close_button.setIcon(qtawesome.icon('mdi.close', scale_factor=1.2))
        self.close_button.setStyleSheet('border: 0px solid transparent;margin-top:4px')
        self.close_button.setVisible(closable)
        self.close_button.clicked.connect(self.close)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(icon_label)
        layout.addWidget(self.content_label)
        layout.addStretch()
        layout.addWidget(self.close_button)

        _close_timer = QtCore.QTimer(self)
        _close_timer.setSingleShot(True)
        _close_timer.timeout.connect(self.close)
        _close_timer.timeout.connect(self.closed)
        _close_timer.setInterval(duration * 1000)

        _ani_timer = QtCore.QTimer(self)
        _ani_timer.timeout.connect(self._fade_out)
        _ani_timer.setInterval(duration * 1000 - 300)

        _close_timer.start()
        _ani_timer.start()

        self._pos_ani = QtCore.QPropertyAnimation(self)
        self._pos_ani.setTargetObject(self)
        self._pos_ani.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self._pos_ani.setDuration(300)
        self._pos_ani.setPropertyName(b'pos')

        self._opacity_ani = QtCore.QPropertyAnimation()
        self._opacity_ani.setTargetObject(self)
        self._opacity_ani.setDuration(300)
        self._opacity_ani.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        self._opacity_ani.setPropertyName(b'windowOpacity')
        self._opacity_ani.setStartValue(0.0)
        self._opacity_ani.setEndValue(1.0)

        self._set_proper_position(parent)
        self._fade_int()

    def _fade_out(self):
        self._pos_ani.setDirection(QtCore.QAbstractAnimation.Backward)
        self._pos_ani.start()
        self._opacity_ani.setDirection(QtCore.QAbstractAnimation.Backward)
        self._opacity_ani.start()

    def _fade_int(self):
        self._pos_ani.start()
        self._opacity_ani.start()

    def _set_proper_position(self, parent):
        parent_geo = parent.geometry()
        pos = (
            parent_geo.topLeft()
            if parent.parent() is None
            else parent.mapToGlobal(parent_geo.topLeft())
        )
        offset = 0
        for child in parent.children():
            if isinstance(child, Message) and child.isVisible():
                offset = max(offset, child.y())
        base = pos.y() + self.top
        target_x = pos.x() + parent_geo.width() / 2 - 100
        target_y = (offset + 50) if offset else base
        self._pos_ani.setStartValue(QtCore.QPoint(target_x, target_y - 40))
        self._pos_ani.setEndValue(QtCore.QPoint(target_x, target_y))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    ms = Message('已成功拷贝', closable=True)
    ms.show()

    app.exec_()
