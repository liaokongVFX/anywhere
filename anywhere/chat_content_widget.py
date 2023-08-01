from datetime import datetime
from uuid import uuid4

import requests
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import qtawesome

from anywhere.widgets import signal_bus, show_message, create_h_spacer_item, create_v_spacer_item
from anywhere.utils import get_config, chat_history_storage


class ChatMessageItem(QtWidgets.QFrame):
    deleted = QtCore.Signal(str)

    def __init__(self, uid, role, text, success=True, parent=None):
        super().__init__(parent)
        self.uid = uid
        self.role = role
        self.text = text
        self.success = success

        self._init_ui()

    def _init_ui(self):
        self.setObjectName('chat_message_item')
        self.setStyleSheet('chat_message_item{border: 1px solid red}')

        header_layout = QtWidgets.QHBoxLayout()

        name = '我' if self.role == 'user' else '机器人'
        info_label = QtWidgets.QLabel('{} {}'.format(name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        header_layout.addWidget(info_label)
        header_layout.addItem(create_h_spacer_item())

        self.reload_button = QtWidgets.QToolButton()
        self.reload_button.setMinimumSize(30, 30)
        self.reload_button.setIcon(qtawesome.icon('mdi6.reload'))

        self.copy_button = QtWidgets.QToolButton()
        self.copy_button.setMinimumSize(30, 30)
        self.copy_button.setIcon(qtawesome.icon('ri.file-copy-fill'))

        self.delete_button = QtWidgets.QToolButton()
        self.delete_button.setMinimumSize(30, 30)
        self.delete_button.setIcon(qtawesome.icon('mdi6.delete-outline'))

        if self.role != 'user':
            header_layout.addWidget(self.reload_button)
        header_layout.addWidget(self.copy_button)
        header_layout.addWidget(self.delete_button)

        self.message_widget = QtWidgets.QTextEdit()
        self.message_widget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.message_widget.setReadOnly(True)
        self.message_widget.setMarkdown(self.text)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addLayout(header_layout)
        layout.addWidget(self.message_widget)

        self.document = self.message_widget.document()
        self.document.contentsChanged.connect(self.message_widget_text_changed)

        self.message_widget_text_changed()

        self.delete_button.clicked.connect(lambda: self.deleted.emit(self.uid))
        self.copy_button.clicked.connect(
            lambda: QtWidgets.QApplication.clipboard().setText(self.text))

    def message_widget_text_changed(self):
        self.document.adjustSize()

        new_height = self.document.size().height() + 10
        if new_height != self.message_widget.height():
            self.message_widget.setFixedHeight(new_height)
            self.setFixedHeight(new_height + 50)


class ChatContentWidget(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_name = None
        self._init_ui()

    def _init_ui(self):
        self._widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self._widget)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.addItem(create_v_spacer_item())

        self.setWidget(self._widget)
        self.setWidgetResizable(True)

    def add_message(self, role, message, success=True):
        item = ChatMessageItem(str(uuid4()), role, message, success)
        item.deleted.connect(self.item_deleted)

        self.layout.insertWidget(self.layout.count() - 1, item)

    def item_deleted(self, uid):
        for index in range(self.layout.count()):
            widget = self.layout.itemAt(index).widget()

            if widget and widget.uid == uid:
                widget.deleteLater()
                chat_history_storage.delete_message_by_index(self.chat_name, index)
                break

    def clear(self):
        for index in range(self.layout.count()):
            widget = self.layout.itemAt(index).widget()

            if widget:
                widget.deleteLater()

    def set_chat_name(self, name):
        self.chat_name = name


class SendMessageThread(QtCore.QThread):
    show_message_signal = QtCore.Signal(dict)

    def __init__(self, messages, config, temperature, parent=None):
        super().__init__(parent)
        self.messages = messages
        self.config = config
        self.temperature = temperature

    def run(self):
        url = self.config.get('proxy', 'https://api.openai.com/v1/chat/completions')
        key = self.config['key']
        model = self.config['model']

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {key}'
        }

        data = {
            'model': model,
            'messages': self.messages,
            "temperature": self.temperature
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            self.show_message_signal.emit({
                'success': True,
                'message': response.json()['choices'][0]['message']
            })
        else:
            self.show_message_signal.emit({
                'success': False,
                'message': {'content': response.json()['message']}
            })


class ChatWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._history_messages = []
        self._history_data = {}

        self._init_ui()

    def _init_ui(self):
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(10, 0, 10, 0)

        self.role_label = QtWidgets.QLabel('角色名：{}'.format('通用'))
        self.token_label = QtWidgets.QLabel('534')
        header_layout.addWidget(self.role_label)

        header_layout.addItem(create_h_spacer_item())
        header_layout.addWidget(QtWidgets.QLabel('token: '))
        header_layout.addWidget(self.token_label)

        self.content_widget = ChatContentWidget()

        self.send_text_widget = QtWidgets.QPlainTextEdit(
            placeholderText='点击右侧按钮或者使用快捷键 Ctrl+Enter 发送消息')
        send_text_shortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence('Ctrl+Return'), self.send_text_widget)
        self.send_button = QtWidgets.QPushButton()
        self.send_button.setIcon(qtawesome.icon('fa.send'))
        self.send_text_widget.setMaximumHeight(60)
        self.send_button.setMaximumHeight(60)
        self.send_button.setMinimumWidth(60)

        send_layout = QtWidgets.QHBoxLayout()
        send_layout.setSpacing(2)
        send_layout.addWidget(self.send_text_widget)
        send_layout.addWidget(self.send_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addLayout(header_layout)
        layout.addWidget(self.content_widget)
        layout.addLayout(send_layout)

        self.send_button.clicked.connect(self.send_message)
        send_text_shortcut.activated.connect(self.send_message)
        signal_bus.history_item_changed.connect(self.history_item_changed)

    def history_item_changed(self, data):
        self._history_data = data
        self.role_label.setText(f'角色名：{data["data"]["role"] or "通用"}')
        self.content_widget.set_chat_name(data['name'])

        _messages = chat_history_storage.get_messages(data['name'])
        if not _messages:
            return

        messages = _messages
        if _messages[0]['role'] == 'system':
            messages = _messages[1:]

        self.content_widget.clear()
        for message in messages:
            self.content_widget.add_message(message['role'], message['content'])

    def send_message(self):
        texts = self.send_text_widget.toPlainText().strip()
        if not texts:
            return show_message('请先输入要发送的内容', 'error')

        config = get_config('common')
        key = config.get('key', '')
        if not key:
            return show_message('请先在公共设置中设置 API Key')

        chat_history_storage.append_messages(
            self._history_data['name'], {'role': 'user', 'content': texts})
        self.content_widget.add_message('user', texts)
        self.send_text_widget.setPlainText('')

        send_message_thread = SendMessageThread(
            chat_history_storage.get_messages(self._history_data['name']),
            config,
            self._history_data['data']['temperature'],
            self
        )
        send_message_thread.show_message_signal.connect(self.show_message)
        send_message_thread.start()

    def show_message(self, data):
        if data['success']:
            chat_history_storage.append_messages(
                self._history_data['name'], data['message'])

        self.content_widget.add_message(
            'bot', data['message']['content'], data['success'])
