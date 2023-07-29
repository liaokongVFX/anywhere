from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui


class NewChatWindow(QtWidgets.QWidget):
    saved = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.name_line = QtWidgets.QLineEdit()
        self.role_combobox = QtWidgets.QComboBox()
        self.save_button = QtWidgets.QPushButton('保存')

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(QtWidgets.QLabel('名称：'), 0, 0)
        layout.addWidget(self.name_line, 0, 1)
        layout.addWidget(QtWidgets.QLabel('角色：'), 1, 0)
        layout.addWidget(self.role_combobox, 1, 1)
        layout.addWidget(self.save_button, 2, 0, 1, 2)

        self.save_button.clicked.connect(self.save_button_clicked)

    def show(self):
        self.name_line.setText('')
        self.role_combobox.setCurrentText('')
        super().show()

    def save_button_clicked(self):
        self.saved.emit({
            'name': self.name_line.text().strip(),
            'rule': self.role_combobox.currentText()
        })
        self.close()


class ChatHistoryWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.new_chat_window = NewChatWindow()

        self.add_button = QtWidgets.QPushButton("新建", minimumHeight=30)
        self.history_list_widget = QtWidgets.QListWidget()
        self.history_list_widget.setFrameShape(QtWidgets.QListWidget.NoFrame)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self.add_button)
        layout.addWidget(self.history_list_widget)

        self.add_button.clicked.connect(self.new_chat_window.show)
        self.new_chat_window.saved.connect(self.new_chat_window_saved)

    def new_chat_window_saved(self):
        pass
