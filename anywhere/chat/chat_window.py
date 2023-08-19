from PySide2 import QtWidgets
from PySide2 import QtCore

from anywhere.chat.chat_history_widget import ChatHistoryWidget
from anywhere.chat.chat_content_widget import ChatWidget


class ChatWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.resize(1000, 800)
        self.setWindowFlags(QtCore.Qt.Dialog |
                            QtCore.Qt.WindowMinMaxButtonsHint |
                            QtCore.Qt.WindowCloseButtonHint)

        self.chat_history_widget = ChatHistoryWidget()
        self.chat_widget = ChatWidget()

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.chat_history_widget)
        splitter.addWidget(self.chat_widget)
        splitter.setSizes([200, 700])

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(splitter)

        self.chat_history_widget.init_data()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    cw = ChatWindow()
    cw.show()

    app.exec_()
