from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from anywhere.utils import CONFIG_PATH


class CommonPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CommonPage, self).__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QGridLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.proxy_line = QtWidgets.QLineEdit(
            placeholderText='请输入代理完整接口，留空则使用OpenAI官方接口地址',
            minimumHeight=30)
        layout.addWidget(QtWidgets.QLabel('代理地址:'), 0, 0)
        layout.addWidget(self.proxy_line, 0, 1)

        self.key_line = QtWidgets.QLineEdit(placeholderText='请输入 API Key', minimumHeight=30)
        self.key_line.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(QtWidgets.QLabel('API Key:'), 1, 0)
        layout.addWidget(self.key_line, 1, 1)

        self.model_line = QtWidgets.QLineEdit('gpt-3.5-turbo', placeholderText='请输入模型全局模型名', minimumHeight=30)
        layout.addWidget(QtWidgets.QLabel('全局模型名:'), 2, 0)
        layout.addWidget(self.model_line, 2, 1)

        layout.addWidget(QtWidgets.QLabel('配置文件位置:'), 3, 0)
        layout.addWidget(QtWidgets.QLabel(CONFIG_PATH, minimumHeight=30), 3, 1)


class PluginPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel('插件配置页面'))


class ConfigWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(ConfigWidget, self).__init__(*args, **kwargs)

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

        self.common_widget = CommonPage(self)
        self.stacked_widget.addWidget(self.common_widget)

        self.plugin_widget = PluginPage(self)
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
