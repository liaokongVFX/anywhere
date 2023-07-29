import os
import json

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from anywhere.utils import get_config, save_config, CONFIG_PATH
from anywhere.widgets import show_message


class CommonPage(QtWidgets.QWidget):
    def __init__(self, config, parent=None):
        super(CommonPage, self).__init__(parent)
        self.config = config

        self._init_ui()

    def _init_ui(self):
        line_layout = QtWidgets.QGridLayout()
        line_layout.setAlignment(QtCore.Qt.AlignTop)

        self.proxy_line = QtWidgets.QLineEdit(
            self.config.get('proxy', ''),
            placeholderText='请输入代理完整接口，留空则使用OpenAI官方接口地址',
            minimumHeight=30)
        line_layout.addWidget(QtWidgets.QLabel('代理地址:'), 0, 0)
        line_layout.addWidget(self.proxy_line, 0, 1)

        self.key_line = QtWidgets.QLineEdit(
            self.config.get('key', ''),
            placeholderText='请输入 API Key',
            minimumHeight=30
        )
        self.key_line.setEchoMode(QtWidgets.QLineEdit.Password)
        line_layout.addWidget(QtWidgets.QLabel('API Key:'), 1, 0)
        line_layout.addWidget(self.key_line, 1, 1)

        self.model_line = QtWidgets.QLineEdit(
            self.config.get('model', 'gpt-3.5-turbo'),
            placeholderText='请输入模型全局模型名',
            minimumHeight=30
        )
        line_layout.addWidget(QtWidgets.QLabel('全局模型名:'), 2, 0)
        line_layout.addWidget(self.model_line, 2, 1)

        self.chat_line = QtWidgets.QLineEdit(
            self.config.get('chat_shortcut', 'Ctrl+Shift+C'),
            placeholderText='请输入呼出聊天窗口快捷键',
            minimumHeight=30
        )
        line_layout.addWidget(QtWidgets.QLabel('聊天快捷键:'), 3, 0)
        line_layout.addWidget(self.chat_line, 3, 1)

        self.menu_line = QtWidgets.QLineEdit(
            self.config.get('menu_shortcut', 'Ctrl+Shift+X'),
            placeholderText='请输入呼出超级菜单快捷键',
            minimumHeight=30
        )
        line_layout.addWidget(QtWidgets.QLabel('超级菜单快捷键:'), 4, 0)
        line_layout.addWidget(self.menu_line, 4, 1)

        line_layout.addWidget(QtWidgets.QLabel('配置文件位置:'), 5, 0)
        path_label = QtWidgets.QLabel(CONFIG_PATH, minimumHeight=30)
        path_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        line_layout.addWidget(path_label, 5, 1)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignRight)
        button_layout.setContentsMargins(0, 26, 16, 0)
        self.save_button = QtWidgets.QPushButton('保存', minimumHeight=34, minimumWidth=86)
        button_layout.addWidget(self.save_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addLayout(line_layout)
        layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.save_button_clicked)

    def save_button_clicked(self):
        data = {
            'proxy': self.proxy_line.text().strip(),
            'key': self.key_line.text().strip(),
            'model': self.model_line.text().strip(),
            'chat_shortcut': self.chat_line.text().strip(),
            'menu_shortcut': self.menu_line.text().strip()
        }
        save_config('common', data)
        show_message('配置保存成功')


class PluginPage(QtWidgets.QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config

        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('插件配置页面'))


class ConfigWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(ConfigWidget, self).__init__(*args, **kwargs)
        self.config = get_config()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Anywhere 配置')
        self.resize(800, 500)
        layout = QtWidgets.QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setMaximumWidth(200)
        layout.addWidget(self.list_widget)

        self.stacked_widget = QtWidgets.QStackedWidget(self)
        layout.addWidget(self.stacked_widget)

        # 初始化界面
        # 通过QListWidget的当前item变化来切换QStackedWidget中的序号
        self.list_widget.currentRowChanged.connect(
            self.stacked_widget.setCurrentIndex)
        # 去掉边框
        self.list_widget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        # 隐藏滚动条
        self.list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.create_list_item('公共配置')
        self.create_list_item('插件配置')

        self.common_widget = CommonPage(self.config.get('common', {}), self)
        self.stacked_widget.addWidget(self.common_widget)

        self.plugin_widget = PluginPage(self.config.get('plugins', {}), self)
        self.stacked_widget.addWidget(self.plugin_widget)

        self.list_widget.setCurrentRow(0)

    def create_list_item(self, name):
        item = QtWidgets.QListWidgetItem(name, self.list_widget)
        item.setSizeHint(QtCore.QSize(67, 50))
        item.setTextAlignment(QtCore.Qt.AlignCenter)


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = ConfigWidget()
    w.show()
    sys.exit(app.exec_())
