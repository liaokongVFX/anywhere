from PySide2 import QtWidgets
from PySide2 import QtCore


def show_message(message, message_type='success', parent=None):
    if message_type == 'success':
        return QtWidgets.QMessageBox.information(parent, '提示', message)
    return QtWidgets.QMessageBox.critical(parent, '提示', message)


class SignalBus(QtCore.QObject):
    """ 全局事件总线 """

    chat_send_message = QtCore.Signal(dict)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(SignalBus, cls).__new__(cls, *args, **kwargs)

        return cls._instance


signal_bus = SignalBus()