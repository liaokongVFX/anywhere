from datetime import datetime

import requests
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import qtawesome

from anywhere.widgets import signal_bus, show_message
from anywhere.utils import get_config


class ChatMessageItem(QtWidgets.QFrame):
    def __init__(self, role, text, success=True, parent=None):
        super().__init__(parent)
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
        header_layout.addItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        )

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

    def message_widget_text_changed(self):
        self.document.adjustSize()

        new_height = self.document.size().height() + 10
        if new_height != self.message_widget.height():
            self.message_widget.setFixedHeight(new_height)
            self.setFixedHeight(new_height + 50)


class ChatContentWidget(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self._widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self._widget)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.addItem(
            QtWidgets.QSpacerItem(0, 0,
                                  QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding
                                  )
        )

        self.setWidget(self._widget)
        self.setWidgetResizable(True)

    def add_message(self, role, message, success=True):
        self.layout.insertWidget(
            self.layout.count() - 1,
            ChatMessageItem(role, message, success)
        )


class SendMessageThread(QtCore.QThread):
    show_message_signal = QtCore.Signal(dict)

    def __init__(self, messages, config, parent=None):
        super().__init__(parent)
        self.messages = messages
        self.config = config

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
            'messages': self.messages
        }
        print(data)

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

        self._init_ui()

    def _init_ui(self):
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(10, 0, 10, 0)

        self.role_label = QtWidgets.QLabel('角色名：{}'.format('通用'))
        self.token_label = QtWidgets.QLabel('534')
        header_layout.addWidget(self.role_label)

        header_layout.addItem(
            QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        )
        header_layout.addWidget(QtWidgets.QLabel('token: '))
        header_layout.addWidget(self.token_label)

        self.content_widget = ChatContentWidget()

        self.send_text_widget = QtWidgets.QPlainTextEdit(
            placeholderText='点击右侧按钮或者使用快捷键 Ctrl+Enter 发送消息')
        send_text_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Return'), self.send_text_widget)
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

    def send_message(self):
        texts = self.send_text_widget.toPlainText().strip()
        if not texts:
            return show_message('请先输入要发送的内容', 'error')

        config = get_config('common')
        key = config.get('key', '')
        if not key:
            return show_message('请先在公共设置中设置 API Key')

        self._history_messages.append({'role': 'user', 'content': texts})
        self.content_widget.add_message('user', texts)
        self.send_text_widget.setPlainText('')

        send_message_thread = SendMessageThread(self._history_messages, config, self)
        send_message_thread.show_message_signal.connect(self.show_message)
        send_message_thread.start()

    def show_message(self, data):
        if data['success']:
            self._history_messages.append(data['message'])

        self.content_widget.add_message('bot', data['message']['content'], data['success'])

