from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
import qtawesome

from anywhere.utils import get_config, save_config, CONFIG_PATH
from anywhere.widgets import show_message, show_question, create_h_spacer_item


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


class NewRoleWindow(QtWidgets.QWidget):
    saved = QtCore.Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.names = []
        self.old_name = None
        self._init_ui()

    def _init_ui(self):
        self.resize(500, 300)

        self.name_line = QtWidgets.QLineEdit(minimumHeight=32)
        self.prompt_widget = QtWidgets.QPlainTextEdit()
        self.save_button = QtWidgets.QPushButton('保存', minimumHeight=34)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(QtWidgets.QLabel('角色名：'), 0, 0)
        layout.addWidget(self.name_line, 0, 1)
        layout.addWidget(QtWidgets.QLabel('Prompt：'), 1, 0)
        layout.addWidget(self.prompt_widget, 1, 1)
        layout.addWidget(self.save_button, 2, 0, 1, 2)

        self.save_button.clicked.connect(self.save_button_clicked)

    def save_button_clicked(self):
        data = {
            'name': self.name_line.text().strip(),
            'prompt': self.prompt_widget.toPlainText().strip(),
            'enabled': True
        }
        if not data['name'] or not data['prompt']:
            return show_message('请输入角色名和Prompt', 'error')

        if data['name'] in self.names:
            return show_message('角色名称已重复', 'error')

        if not self.old_name:
            save_config('role', data, data_type='list')
        else:
            old_data = get_config('role', 'list')
            for index in range(len(old_data)):
                if old_data[index]['name'] == self.old_name:
                    old_data[index] = data
                    break
            save_config('role', old_data, data_type='list', is_set=True)

        data['old_name'] = self.old_name
        self.saved.emit(data)
        self.close()

    def show_window(self):
        self.names = [r['name'] for r in get_config('role', 'list')]
        self.setWindowTitle('添加角色')
        self.name_line.setText('')
        self.prompt_widget.setPlainText('')
        self.old_name = None
        self.show()

    def show_edit_window(self, name, prompt):
        self.names = [r['name'] for r in get_config('role', 'list')]
        self.setWindowTitle('编辑角色')
        self.name_line.setText(name)
        self.prompt_widget.setPlainText(prompt)
        self.old_name = name
        self.show()


class RoleItem(QtWidgets.QWidget):
    deleted = QtCore.Signal(str)
    edited = QtCore.Signal(str)
    check_changed = QtCore.Signal(tuple)

    def __init__(self, enabled, name, parent=None):
        super().__init__(parent)
        self.enabled = enabled
        self.name = name

        self._init_ui()

    def _init_ui(self):
        self.enabled_checkbox = QtWidgets.QCheckBox()
        self.enabled_checkbox.setChecked(self.enabled)
        self.name_label = QtWidgets.QLabel(self.name)
        self.edit_button = QtWidgets.QToolButton()
        self.edit_button.setIcon(qtawesome.icon('fa5.edit'))
        self.edit_button.setMinimumSize(24, 24)
        self.delete_button = QtWidgets.QToolButton()
        self.delete_button.setIcon(qtawesome.icon('mdi6.delete-outline'))
        self.delete_button.setMinimumSize(24, 24)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.enabled_checkbox)
        layout.addWidget(self.name_label)
        layout.addItem(create_h_spacer_item())
        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)

        self.delete_button.clicked.connect(self.delete_button_clicked)
        self.edit_button.clicked.connect(lambda: self.edited.emit(self.name))
        self.enabled_checkbox.stateChanged.connect(
            lambda: self.check_changed.emit((self.name, self.enabled_checkbox.isChecked())))

    def delete_button_clicked(self):
        if show_question(f'确定要删除角色 {self.name} 吗？'):
            self.deleted.emit(self.name)

    def set_name(self, name):
        self.name_label.setText(name)
        self.name = name


class RolePage(QtWidgets.QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._init_ui()
        self._init_data()

    def _init_ui(self):
        self.new_role_widget = NewRoleWindow()

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setAlignment(QtCore.Qt.AlignRight)
        add_button = QtWidgets.QPushButton('添加', minimumHeight=34, minimumWidth=86)
        header_layout.addWidget(add_button)

        self.role_list_widget = QtWidgets.QListWidget()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(header_layout)
        layout.addWidget(self.role_list_widget)

        add_button.clicked.connect(self.new_role_widget.show_window)
        self.new_role_widget.saved.connect(self.new_role_widget_saved)

    def _init_data(self):
        for data in self.config:
            self.add_item(data)

    def new_role_widget_saved(self, data):
        old_name = data.pop('old_name', None)
        if not old_name:
            self.add_item(data)
        else:
            for row in range(self.role_list_widget.count()):
                item = self.role_list_widget.item(row)
                if item.name == old_name:
                    item.name = data['name']
                    item.prompt = data['prompt']
                    item.setToolTip(item.prompt)
                    widget = self.role_list_widget.itemWidget(item)
                    widget.set_name(item.name)

                    self.config = get_config('role', 'list')
                    break

    def add_item(self, data):
        item = QtWidgets.QListWidgetItem()
        item.prompt = data['prompt']
        item.name = data['name']
        item.setSizeHint(QtCore.QSize(50, 40))
        item.setToolTip(item.prompt)
        widget = RoleItem(data['enabled'], item.name)
        self.role_list_widget.addItem(item)
        self.role_list_widget.setItemWidget(item, widget)

        widget.deleted.connect(self.role_item_deleted)
        widget.edited.connect(self.role_item_edited)
        widget.check_changed.connect(self.role_item_check_changed)

        self.config = get_config('role', 'list')

    def role_item_check_changed(self, data):
        name, checked = data
        for config in self.config:
            if config['name'] == name:
                config['enabled'] = checked

        save_config('role', self.config, 'list', True)

    def role_item_edited(self, name):
        for row in range(self.role_list_widget.count()):
            item = self.role_list_widget.item(row)
            if item.name == name:
                self.new_role_widget.show_edit_window(name, item.prompt)
                break

    def role_item_deleted(self, name):
        for row in range(self.role_list_widget.count()):
            item = self.role_list_widget.item(row)
            if item.name == name:
                self.role_list_widget.takeItem(row)
                break

        for data in self.config:
            if data['name'] == name:
                self.config.remove(data)
                save_config('role', self.config, 'list', True)
                break


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
        self.create_list_item('角色配置')
        self.create_list_item('插件配置')

        self.common_widget = CommonPage(self.config.get('common', {}), self)
        self.stacked_widget.addWidget(self.common_widget)

        self.role_widget = RolePage(self.config.get('role', {}), self)
        self.stacked_widget.addWidget(self.role_widget)

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
