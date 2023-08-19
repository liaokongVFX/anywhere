import sys

from PySide2 import QtWidgets
from PySide2 import QtGui

from anywhere.config_window import ConfigWidget
from anywhere.chat.chat_window import ChatWindow
from anywhere.widgets import signal_bus
from anywhere.utils import get_config
from anywhere.hotkey import HotkeyThread


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.setToolTip('Chuangyi Sitter')
        self.setIcon(QtGui.QIcon('resources/images/publish.png'))

        self.config_widget = ConfigWidget()
        self.chat_window = ChatWindow()
        self.hotkey_thread = None

        self._config_saved()

        self.create_tray_menu()
        self._connect()

        self._init_hotkey()

        self.bubble('托盘启动成功！')

    def _connect(self):
        signal_bus.config_saved.connect(self._config_saved)

    def _init_hotkey(self):
        config = get_config('common')

        shortcut_map = {}
        chat_shortcut = config.get('chat_shortcut')
        if chat_shortcut:
            shortcut_map.update({chat_shortcut: 'show_chat'})

        if shortcut_map:
            self.hotkey_thread = HotkeyThread(shortcut_map, self)
            self.hotkey_thread.shortcut_triggered.connect(self._shortcut_triggered)
            self.hotkey_thread.start()

    def _shortcut_triggered(self, action_name):
        action_map = {
            'show_chat': self.chat_window.show
        }
        action_map[action_name]()

    def _config_saved(self):
        if self.hotkey_thread:
            self.hotkey_thread.terminate()
            self.hotkey_thread = None

        self._init_hotkey()

    def create_tray_menu(self):
        self.tray_menu = QtWidgets.QMenu()

        self.config_action = QtWidgets.QAction(
            '配置', triggered=self.config_widget.show)
        self.quit_action = QtWidgets.QAction(
            '退出', triggered=QtWidgets.QApplication.quit
        )

        self.tray_menu.addAction(self.config_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.quit_action)
        self.setContextMenu(self.tray_menu)

    def bubble(self, text, title='Anywhere 通知'):
        self.showMessage(title, text, self.icon())


class Tray(QtWidgets.QApplication):
    def __init__(self):
        super(Tray, self).__init__(sys.argv)
        self.setQuitOnLastWindowClosed(False)

        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()

    def run(self):
        sys.exit(self.exec_())


if __name__ == '__main__':
    tray = Tray()
    tray.run()
