from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import qtawesome

from anywhere.utils import chat_history_storage, get_config
from anywhere.widgets import show_message, show_question, signal_bus


class NewChatWindow(QtWidgets.QWidget):
    saved = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.old_name = None
        self.prompt_by_role = {}
        self._init_ui()

    def _init_ui(self):
        self.resize(300, 160)

        self.name_line = QtWidgets.QLineEdit(minimumHeight=30)
        self.role_combobox = QtWidgets.QComboBox(minimumHeight=30)
        self.description_line = QtWidgets.QLineEdit(minimumHeight=30)
        self.temperature_line = QtWidgets.QDoubleSpinBox(minimumHeight=30)
        self.temperature_line.setRange(0, 1)
        self.temperature_line.setSingleStep(0.1)
        self.temperature_line.setDecimals(1)
        self.save_button = QtWidgets.QPushButton('保存', minimumHeight=34)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(QtWidgets.QLabel('名称：'), 0, 0)
        layout.addWidget(self.name_line, 0, 1)
        layout.addWidget(QtWidgets.QLabel('角色：'), 1, 0)
        layout.addWidget(self.role_combobox, 1, 1)
        layout.addWidget(QtWidgets.QLabel('描述：'), 2, 0)
        layout.addWidget(self.description_line, 2, 1)
        layout.addWidget(QtWidgets.QLabel('温度：'), 3, 0)
        layout.addWidget(self.temperature_line, 3, 1)
        layout.addWidget(self.save_button, 4, 0, 1, 2)

        self.save_button.clicked.connect(self.save_button_clicked)

    def show_window(self, count):
        self.prompt_by_role = {
            x['name']: x['prompt']
            for x in get_config('role', 'list')
            if x['enabled']
        }

        self.setWindowTitle('创建聊天')
        self.name_line.setText(f'新聊天{count}')

        self.role_combobox.clear()
        self.role_combobox.addItems([''] + list(self.prompt_by_role.keys()))
        self.role_combobox.setCurrentText('')

        self.description_line.setText('')
        self.temperature_line.setValue(0.6)
        self.old_name = None
        self.show()

    def show_edit_window(self, name, config):
        self.prompt_by_role = {
            x['name']: x['prompt']
            for x in get_config('role', 'list')
            if x['enabled']
        }

        self.setWindowTitle('编辑聊天')
        self.name_line.setText(name)

        self.role_combobox.clear()
        self.role_combobox.addItems([''] + list(self.prompt_by_role.keys()))

        self.role_combobox.setCurrentText(config.get('role', ''))
        self.description_line.setText(config.get('description', ''))
        self.temperature_line.setValue(config.get('temperature', 0.6))
        self.old_name = name
        self.show()

    def save_button_clicked(self):
        name = self.name_line.text().strip()
        if not name:
            return show_message('请设置名称', 'error')

        if not self.old_name and name in chat_history_storage.get_history_names():
            return show_message('名字已存在', 'error')

        self.saved.emit({
            'name': self.name_line.text().strip(),
            'role': self.role_combobox.currentText(),
            'description': self.description_line.text().strip(),
            'temperature': self.temperature_line.value(),
            'old_name': self.old_name,
            'prompt': self.prompt_by_role.get(self.role_combobox.currentText(), '')
        })
        self.close()


class HistoryItem(QtWidgets.QWidget):
    deleted = QtCore.Signal(str)
    edited = QtCore.Signal(str)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name

        self.name_label = QtWidgets.QLabel(name)
        self.edit_button = QtWidgets.QToolButton()
        self.edit_button.setIcon(qtawesome.icon('fa5.edit'))
        self.edit_button.setMinimumSize(24, 24)
        self.delete_button = QtWidgets.QToolButton()
        self.delete_button.setIcon(qtawesome.icon('mdi6.delete-outline'))
        self.delete_button.setMinimumSize(24, 24)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(10, 2, 8, 2)
        layout.addWidget(self.name_label)
        layout.addItem(
            QtWidgets.QSpacerItem(
                0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        )
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)

        self.edit_button.clicked.connect(lambda: self.edited.emit(self.name))
        self.delete_button.clicked.connect(self.delete_button_clicked)

    def delete_button_clicked(self):
        if show_question(f'确定要删除 {self.name} 中的所有对话信息?'):
            self.deleted.emit(self.name)

    def set_name(self, name):
        self.name = name
        self.name_label.setText(name)


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

        self.add_button.clicked.connect(
            lambda: self.new_chat_window.show_window(
                self.history_list_widget.count() + 1)
        )
        self.new_chat_window.saved.connect(self.new_chat_window_saved)
        self.history_list_widget.currentRowChanged.connect(self.history_list_row_changed)

    def history_list_row_changed(self, row):
        name = self.history_list_widget.item(row).name
        data = chat_history_storage.get_common_config(name)
        signal_bus.history_item_changed.emit({'name': name, 'data': data})

    def init_data(self):
        histories = chat_history_storage.get_histories()
        if not histories:
            return

        for name, data in histories.items():
            self.add_item(name, data['common'])

        self.history_list_widget.setCurrentRow(0)

    def new_chat_window_saved(self, data):
        old_name = data.pop('old_name')
        name = data.pop('name')
        prompt = data.pop('prompt')
        if not old_name:
            self.add_item(name, data)
            chat_history_storage.set_common_config(name, data)
            self.history_list_widget.setCurrentRow(
                self.history_list_widget.count() - 1)
            if prompt:
                chat_history_storage.set_system_message(name, prompt)

        else:
            for index in range(self.history_list_widget.count()):
                item = self.history_list_widget.item(index)
                if item.name == old_name:
                    item.name = name
                    item.setToolTip(data['description'])

                    if old_name == name:
                        chat_history_storage.set_common_config(name, data)
                    else:
                        widget = self.history_list_widget.itemWidget(item)
                        widget.set_name(name)
                        chat_history_storage.change_common_config_name(old_name, name, data)

                    chat_history_storage.set_system_message(name, prompt)
                    break

    def add_item(self, name, data):
        item = QtWidgets.QListWidgetItem()
        item.name = name
        item.setSizeHint(QtCore.QSize(50, 40))
        item.setToolTip(data['description'])
        widget = HistoryItem(name)
        self.history_list_widget.addItem(item)
        self.history_list_widget.setItemWidget(item, widget)

        widget.edited.connect(self.history_edited)
        widget.deleted.connect(self.history_deleted)

    def history_edited(self, name):
        config = chat_history_storage.get_common_config(name)
        self.new_chat_window.show_edit_window(name, config)

    def history_deleted(self, name):
        for index in range(self.history_list_widget.count()):
            item = self.history_list_widget.item(index)
            if item.name == name:
                self.history_list_widget.takeItem(index)
                chat_history_storage.delete_history(name)
                break
