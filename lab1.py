#!/usr/bin/env python3

import shutil
import sys
import os
import re
from subprocess import call
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QWidget, QMessageBox


class User:
    def __init__(self, name):
        self.name = name
        if name == "admin":
            self.group = "admin"
        else:
            self.group = "users"

        self.permitted_operations = []
        if self.group == "admin":
            self.permitted_operations = ["pwd", "ls", "cd", "mkdir", "vi", "rm"]
        else:
            self.permitted_operations = ["pwd", "ls", "cd"]


class Terminal(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.window_width, self.window_height = 800, 550
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle('Термінал')

        font = QtGui.QFont()
        font.setPointSize(12)

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 791, 541))

        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.lineEdit_command = QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_command.setFont(font)
        self.verticalLayout.addWidget(self.lineEdit_command)

        self.button_run = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_run.setFont(font)
        self.button_run.setText("Run")
        self.verticalLayout.addWidget(self.button_run)
        self.button_run.clicked.connect(self.check_command)

        self.textBrowser = QtWidgets.QTextBrowser(self.verticalLayoutWidget)
        self.textBrowser.setFont(font)
        self.verticalLayout.addWidget(self.textBrowser)

        self.path = '/home/diana/calculator'

    def check_command(self):
        os.chdir(self.path)
        input_line = self.lineEdit_command.text().strip()
        input_command = input_line.split()[0]
        if input_command in self.user.permitted_operations:
            self.run(input_line)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Помилка")
            msg.setText("Вам відмовлено у доступі!")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()

    def run(self, input_line):
        if input_line == "pwd":
            self.textBrowser.clear()
            output = os.getcwd()
            self.textBrowser.setPlainText(output)
        elif input_line == "ls":
            self.textBrowser.clear()
            output = os.listdir(os.getcwd())
            for i in output:
                self.textBrowser.append(i)
        elif "cd" in input_line:
            change_path = input_line.split()
            if change_path[1] == "..":
                self.path = re.sub("/(?:.(?!/))+$", "", self.path)
            else:
                self.path = self.path + "/" + change_path[1]
            self.textBrowser.clear()
            os.chdir(self.path)
            self.textBrowser.setPlainText(os.getcwd())
        elif "mkdir" in input_line:
            make_dir = input_line.split()
            self.textBrowser.clear()
            os.mkdir(os.getcwd() + "/" + make_dir[1])
            output = "created " + make_dir[1]
            self.textBrowser.setPlainText(output)
        elif "vi" in input_line:
            EDITOR = os.environ.get('EDITOR', 'vim')
            file = input_line.split()
            if len(file) == 1:
                call([EDITOR])
            else:
                file_name = file[1]
                call([EDITOR, file_name])
        elif "rm" in input_line:
            rm_path = input_line.split()
            self.textBrowser.clear()
            path = self.path + "/" + rm_path[1]
            if os.path.isfile(path):
                os.remove(path)
            if os.path.isdir(path):
                shutil.rmtree(path)
            output = "removed " + rm_path[1]
            self.textBrowser.setPlainText(output)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 750, 350
        self.setMinimumSize(self.window_width, self.window_height)

        self.setWindowTitle('Вхід в систему')

        font = QtGui.QFont()
        font.setPointSize(13)

        self.lineEdit_login = QLineEdit(self)
        self.lineEdit_login.setGeometry(QtCore.QRect(300, 32, 330, 50))
        self.lineEdit_login.setFont(font)

        self.button_enter = QPushButton(self)
        self.button_enter.setGeometry(QtCore.QRect(30, 200, 170, 70))
        self.button_enter.setFont(font)
        self.button_enter.setText("Вхід")
        self.button_enter.clicked.connect(self.enter)

        self.label_login = QtWidgets.QLabel(self)
        self.label_login.setGeometry(QtCore.QRect(20, 30, 250, 50))
        self.label_login.setFont(font)
        self.label_login.setText("Введіть логін:")

    def enter(self):
        input_login = self.lineEdit_login.text().strip()
        user = User(input_login)
        self.close()
        terminal = Terminal(user)
        terminal.show()
        self.exec_()


if __name__ == "__main__":
    os.chmod('/home/diana/calculator', 0o000)
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    app.exec_()
    os.chmod('/home/diana/calculator', 0o775)
    sys.exit()
