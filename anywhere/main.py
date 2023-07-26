import sys

from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

from anywhere.config_window import ConfigWidget


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.setToolTip('Chuangyi Sitter')
        self.setIcon(QtGui.QIcon('publish.png'))

        self.config_widget = ConfigWidget()

        self.create_tray_menu()

        self.bubble('托盘启动成功！')

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
