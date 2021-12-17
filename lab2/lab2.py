#!/usr/bin/env python3

import shutil
import sys
import os
import re
import json
from math import sqrt
import datetime
from subprocess import call
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QWidget, QMessageBox
from random import choice


class User:
    def __init__(self, login, idx):
        with open(adm_path + '/journal.json', 'r') as file:
            journal = json.load(file)
        self.idx = idx
        self.login = login
        self.password = journal["users"][self.idx]["password"]
        self.date = journal["users"][self.idx]["date"]
        self.permissions = journal["users"][self.idx]["permissions"]
        self.question = journal["users"][self.idx]["question"]
        self.answer = journal["users"][self.idx]["answer"]

        self.permitted_operations = []
        if self.permissions['R'] == 1:
            self.permitted_operations.append('pwd')
            self.permitted_operations.append('ls')
        if self.permissions['W'] == 1:
            self.permitted_operations.append('vi')
            self.permitted_operations.append('mkdir')
            self.permitted_operations.append('rm')
        if self.permissions['X'] == 1:
            self.permitted_operations.append('cd')


class Terminal(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.window_width, self.window_height = 800, 550
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle('Термінал')

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 791, 541))

        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.lineEdit_command = QLineEdit(self.verticalLayoutWidget)
        self.verticalLayout.addWidget(self.lineEdit_command)

        self.button_run = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button_run.setText("Run")
        self.verticalLayout.addWidget(self.button_run)
        self.button_run.clicked.connect(self.check_command)

        self.textBrowser = QtWidgets.QTextBrowser(self.verticalLayoutWidget)
        self.verticalLayout.addWidget(self.textBrowser)

        self.path = path

        QTimer.singleShot(60000, self.timer_func)    # 1 minute

    def timer_func(self):
        self.close()
        auth_w = AuthenticationWindow(self.user)
        auth_w.show()
        self.exec_()

    def check_command(self):
        os.chdir(self.path)
        input_line = self.lineEdit_command.text().strip()
        input_command = input_line.split()[0]
        if input_command not in self.user.permitted_operations or "admin" in input_line:
            show_error("Вам відмовлено у доступі!")
        else:
            self.run(input_line)

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


class EnterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 750, 350
        self.setMinimumSize(self.window_width, self.window_height)

        self.setWindowTitle('Вхід в систему')

        self.lineEdit_login = QLineEdit(self)
        self.lineEdit_login.setGeometry(QtCore.QRect(350, 32, 330, 50))

        self.button_enter = QPushButton(self)
        self.button_enter.setGeometry(QtCore.QRect(30, 200, 170, 70))
        self.button_enter.setText("Вхід")
        self.button_enter.clicked.connect(self.enter)

        self.label_login = QtWidgets.QLabel(self)
        self.label_login.setGeometry(QtCore.QRect(20, 30, 300, 50))
        self.label_login.setText("Введіть логін:")

        self.label_password = QtWidgets.QLabel(self)
        self.label_password.setGeometry(QtCore.QRect(20, 90, 300, 50))
        self.label_password.setText("Введіть пароль:")

        self.lineEdit_password = QLineEdit(self)
        self.lineEdit_password.setGeometry(QtCore.QRect(350, 92, 330, 50))
        self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)

    def enter(self):
        input_login = self.lineEdit_login.text().strip()
        input_pass = self.lineEdit_password.text().strip()

        with open(adm_path + '/journal.json', 'r') as file:
            journal = json.load(file)

        found = False
        idx = -1
        for user in journal["users"]:
            idx += 1
            if user["login"] == input_login and user["password"] == input_pass:
                if input_login == "admin":
                    adm_w = AdminWindow()
                    adm_w.show()
                    self.close()
                    found = True
                    break
                else:
                    cur_user = User(input_login, idx)
                    auto_w = AuthenticationWindow(cur_user)
                    auto_w.show()
                    found = True
                    self.close()
                    break

        if not found:
            show_error("Неправильний логін або пароль!")
        self.exec_()


class AuthenticationWindow(QWidget):
    def __init__(self, cur_user):
        super().__init__()
        self.cur_user = cur_user
        self.func_x = [i * i + 28 for i in range(2, 12)]
        self.if_qst = False
        rand = choice([0, 1])
        if rand == 0:
            with open(adm_path + '/questions.json', 'r') as file:
                questions = json.load(file)
            self.label = questions["questions"][0][self.cur_user.question]
            self.if_qst = True
        else:
            self.x = choice(self.func_x)
            self.label = f'Введіть відповідь для f({self.x})'

        self.setWindowTitle("Аутентифікація")
        self.resize(600, 400)

        self.label_quest = QtWidgets.QLabel(self)
        self.label_quest.setGeometry(QtCore.QRect(40, 20, 510, 50))
        self.label_quest.setText(self.label)

        self.line_answ = QtWidgets.QLineEdit(self)
        self.line_answ.setGeometry(QtCore.QRect(40, 100, 300, 50))

        self.but_ok = QtWidgets.QPushButton(self)
        self.but_ok.setGeometry(QtCore.QRect(40, 250, 150, 50))
        self.but_ok.setText("ОК")
        self.but_ok.clicked.connect(self.ok)

        self.but_canc = QtWidgets.QPushButton(self)
        self.but_canc.setGeometry(QtCore.QRect(250, 250, 150, 50))
        self.but_canc.setText("Cancel")
        self.but_canc.clicked.connect(self.cancel)

    def ok(self):
        input_answ = self.line_answ.text().strip()
        if self.if_qst:
            if self.cur_user.answer != input_answ:
                self.close()
                show_error("Неправильна відповідь!")
                self.check_errors()
                ent = EnterWindow()
                ent.show()
            else:
                self.close()
                x = check_change_pass(self.cur_user, change_pass)
                if x:
                    change_w = ChangePass(self.cur_user)
                    change_w.show()
                    t = Terminal(self.cur_user)
                    t.show()
                else:
                    t = Terminal(self.cur_user)
                    t.show()
        else:
            calc_answ = func(self.x)
            if calc_answ != int(input_answ):
                self.close()
                show_error("Неправильна відповідь!")
                self.check_errors()
                ent = EnterWindow()
                ent.show()
            else:
                self.close()
                x = check_change_pass(self.cur_user, change_pass)
                if x:
                    change_w = ChangePass(self.cur_user)
                    change_w.show()
                    t = Terminal(self.cur_user)
                    t.show()
                else:
                    t = Terminal(self.cur_user)
                    t.show()
        self.exec_()

    def cancel(self):
        self.close()
        ent = EnterWindow()
        ent.show()

    def check_errors(self):
        check_login = self.cur_user.login
        with open(adm_path + '/journal.json', 'r') as file:
            journal = json.load(file)
        idx = 0
        while journal["users"][idx]["login"] != check_login:
            idx += 1

        journal["users"][idx]["auth_errors"] += 1

        if journal["users"][idx]["auth_errors"] >= auth_errors:
            journal["users"].pop(idx)

            with open(adm_path + '/journal.json', 'w', encoding='utf-8') as file:
                json.dump(journal, file, indent=3)

            os.chmod(path, 0o775)
            sys.exit()

        else:
            with open(adm_path + '/journal.json', 'w', encoding='utf-8') as file:
                json.dump(journal, file, indent=3)


class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вікно адміністратора")
        self.resize(1000, 800)

        self.centralwidget = QtWidgets.QWidget(self)

        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(20, 30, 1000, 800))

        self.home_page = QtWidgets.QWidget()
        self.add_user = QtWidgets.QPushButton(self.home_page)
        self.add_user.setGeometry(QtCore.QRect(210, 80, 550, 70))
        self.add_user.setText("Додати нового користувача")
        self.add_user.clicked.connect(self.show_add)

        self.delete_user = QtWidgets.QPushButton(self.home_page)
        self.delete_user.setGeometry(QtCore.QRect(210, 170, 550, 70))
        self.delete_user.setText("Видалити користувача")
        self.delete_user.clicked.connect(self.show_del)

        self.stackedWidget.addWidget(self.home_page)
        #----------------- add page -----------------
        self.add_page = QtWidgets.QWidget()
        self.label_login = QtWidgets.QLabel(self.add_page)
        self.label_login.setGeometry(QtCore.QRect(70, 50, 141, 40))
        self.label_login.setText("Логін")

        self.line_login = QtWidgets.QLineEdit(self.add_page)
        self.line_login.setGeometry(QtCore.QRect(230, 50, 300, 40))

        self.label_pass = QtWidgets.QLabel(self.add_page)
        self.label_pass.setGeometry(QtCore.QRect(70, 100, 140, 40))
        self.label_pass.setText("Пароль")

        self.line_pass = QtWidgets.QLineEdit(self.add_page)
        self.line_pass.setGeometry(QtCore.QRect(230, 100, 300, 40))
        self.line_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.label_date = QtWidgets.QLabel(self.add_page)
        self.label_date.setGeometry(QtCore.QRect(70, 150, 300, 40))
        self.label_date.setText("Дата регістрації")

        self.line_date = QtWidgets.QLineEdit(self.add_page)
        self.line_date.setGeometry(QtCore.QRect(370, 150, 300, 40))

        self.label_permiss = QtWidgets.QLabel(self.add_page)
        self.label_permiss.setGeometry(QtCore.QRect(70, 200, 300, 40))
        self.label_permiss.setText("Права доступу")

        self.box_r = QtWidgets.QCheckBox('R', self.add_page)
        self.box_r.setGeometry(QtCore.QRect(370, 200, 75, 40))

        self.box_w = QtWidgets.QCheckBox('W', self.add_page)  # 430
        self.box_w.setGeometry(QtCore.QRect(460, 200, 75, 40))

        self.box_x = QtWidgets.QCheckBox('X', self.add_page)  # 490
        self.box_x.setGeometry(QtCore.QRect(550, 200, 75, 40))

        self.label_quest = QtWidgets.QLabel(self.add_page)
        self.label_quest.setGeometry(QtCore.QRect(70, 250, 360, 40))
        self.label_quest.setText("Контрольне питання")

        self.line_quest = QtWidgets.QLineEdit(self.add_page)
        self.line_quest.setGeometry(QtCore.QRect(70, 300, 40, 40))

        self.line_answer = QtWidgets.QLineEdit(self.add_page)
        self.line_answer.setGeometry(QtCore.QRect(140, 300, 120, 40))

        self.but_add_user = QtWidgets.QPushButton(self.add_page)
        self.but_add_user.setGeometry(QtCore.QRect(70, 370, 370, 80))
        self.but_add_user.setText("Додати користувача")
        self.but_add_user.clicked.connect(self.to_add_user)

        self.but_clear = QtWidgets.QPushButton(self.add_page)
        self.but_clear.setGeometry(QtCore.QRect(450, 370, 370, 80))
        self.but_clear.setText("Очистити")
        self.but_clear.clicked.connect(self.to_clear)

        self.but_del_user = QtWidgets.QPushButton(self.add_page)
        self.but_del_user.setGeometry(QtCore.QRect(70, 470, 350, 80))
        self.but_del_user.setText("Назад")
        self.but_del_user.clicked.connect(self.return_home)

        self.stackedWidget.addWidget(self.add_page)

        #-------------------- delete page --------------------
        self.delete_page = QtWidgets.QWidget()

        self.label_del_login = QtWidgets.QLabel(self.delete_page)
        self.label_del_login.setGeometry(QtCore.QRect(70, 100, 300, 40))
        self.label_del_login.setText("Введіть логін")

        self.line_del_login = QtWidgets.QLineEdit(self.delete_page)
        self.line_del_login.setGeometry(QtCore.QRect(70, 170, 300, 60))

        self.but_del_user = QtWidgets.QPushButton(self.delete_page)
        self.but_del_user.setGeometry(QtCore.QRect(70, 300, 430, 80))
        self.but_del_user.setText("Видалити користувача")
        self.but_del_user.clicked.connect(self.to_del_user)

        self.but_del_user = QtWidgets.QPushButton(self.delete_page)
        self.but_del_user.setGeometry(QtCore.QRect(510, 300, 350, 80))
        self.but_del_user.setText("Назад")
        self.but_del_user.clicked.connect(self.return_home)

        self.stackedWidget.addWidget(self.delete_page)
        self.setCentralWidget(self.centralwidget)

    def show_add(self):
        self.stackedWidget.setCurrentWidget(self.add_page)

    def show_del(self):
        self.stackedWidget.setCurrentWidget(self.delete_page)

    def return_home(self):
        self.stackedWidget.setCurrentWidget(self.home_page)

    def to_clear(self):
        self.line_login.clear()
        self.line_pass.clear()
        self.line_date.clear()
        self.line_quest.clear()
        self.line_answer.clear()
        self.box_r.setChecked(False)
        self.box_w.setChecked(False)
        self.box_x.setChecked(False)

    def to_add_user(self):
        login = self.line_login.text().strip()
        password = self.line_pass.text().strip()
        date = self.line_date.text().strip()

        permiss = [0, 0, 0]
        if self.box_r.isChecked():
            permiss[0] = 1
        if self.box_w.isChecked():
            permiss[1] = 1
        if self.box_x.isChecked():
            permiss[2] = 1

        question = self.line_quest.text().strip()
        answer = self.line_answer.text().strip()

        if check_passw(password, passw_len):
            show_error("Короткий пароль!")
        elif int(question) > 5 or int(question) < 1:
            show_error("Неправильний номер питання!")
        else:
            with open(adm_path + '/journal.json', 'r') as file:
                journal = json.load(file)
            if len(journal["users"]) - 1 >= users_number:
                show_error("Занадто багато користувачів!")
            else:
                journal["users"].append({"login": login,
                                         "password": password,
                                         "date": date,
                                         "permissions": {"R": permiss[0], "W": permiss[1], "X": permiss[2]},
                                         "question": question,
                                         "answer": answer,
                                         "auth_errors": 0})
                with open(adm_path + '/journal.json', 'w', encoding='utf-8') as file:
                    json.dump(journal, file, indent=3)

    def to_del_user(self):
        del_login = self.line_del_login.text().strip()
        with open(adm_path + '/journal.json', 'r') as file:
            journal = json.load(file)
        idx = 0
        while journal["users"][idx]["login"] != del_login:
            idx += 1
        journal["users"].pop(idx)
        with open(adm_path + '/journal.json', 'w', encoding='utf-8') as file:
            json.dump(journal, file, indent=3)


class ChangePass(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Необхідно змінити пароль")
        self.resize(700, 400)

        self.label_old = QtWidgets.QLabel(self)
        self.label_old.setGeometry(QtCore.QRect(50, 40, 280, 40))
        self.label_old.setText("Старий пароль")

        self.label_new = QtWidgets.QLabel(self)
        self.label_new.setGeometry(QtCore.QRect(50, 120, 280, 40))
        self.label_new.setText("Новий пароль")

        self.line_old = QtWidgets.QLineEdit(self)
        self.line_old.setGeometry(QtCore.QRect(350, 40, 250, 40))
        self.line_old.setEchoMode(QLineEdit.EchoMode.Password)

        self.line_new = QtWidgets.QLineEdit(self)
        self.line_new.setGeometry(QtCore.QRect(350, 120, 250, 40))
        self.line_new.setEchoMode(QLineEdit.EchoMode.Password)

        self.but_ok = QtWidgets.QPushButton(self)
        self.but_ok.setGeometry(QtCore.QRect(50, 250, 150, 50))
        self.but_ok.setText("OK")
        self.but_ok.clicked.connect(self.ok)

        self.but_canc = QtWidgets.QPushButton(self)
        self.but_canc.setGeometry(QtCore.QRect(300, 250, 150, 50))
        self.but_canc.setText("Cancel")
        self.but_canc.clicked.connect(self.cancel)

    def ok(self):
        inp_old_pass = self.line_old.text().strip()
        inp_new_pass = self.line_new.text().strip()

        if inp_old_pass != self.user.password:
            show_error("Неправильний пароль!")
        elif check_passw(inp_new_pass, passw_len):
            show_error("Короткий пароль!")
        else:
            with open(adm_path + '/journal.json', 'r') as file:
                journal = json.load(file)
            journal["users"][self.user.idx]["password"] = inp_new_pass
            journal["users"][self.user.idx]["date"] = datetime.date.today().strftime('%d.%m.%Y')
            with open(adm_path + '/journal.json', 'w', encoding='utf-8') as file:
                json.dump(journal, file, indent=3)
            self.close()

    def cancel(self):
        self.close()


func = lambda x: int(sqrt(x - 28))


def show_error(mes):
    msg = QMessageBox()
    msg.setWindowTitle("Помилка")
    msg.setText(mes)
    msg.setIcon(QMessageBox.Critical)
    msg.exec_()


def check_change_pass(user, change_pass):
    date_list = list(map(int, re.split("[.]", user.date)))
    user_date = datetime.date(date_list[2], date_list[1], date_list[0])
    cur_date = datetime.date.today()
    delta = datetime.timedelta(days=change_pass)
    user_date += delta
    if user_date < cur_date:
        return True
    return False


def check_passw(passw, length):
    return len(passw) < length


def create_journal():
    journal = {"users": [{"login": "admin", "password": "passwordpassword"}]}

    with open(adm_path + '/journal.json', 'w', encoding='utf-8') as file:
        json.dump(journal, file, indent=3)


def create_questions():
    questions = {"questions": [{
        "1": "Яке ім'я вашої собаки?",
        "2": "Яке дівоче прізвище вашої матері?",
        "3": "Скільки вам років?",
        "4": "Скільки у вас дітей?",
        "5": "Яке ім'я вашого кота?"
    }]}

    with open(adm_path + '/questions.json', 'w', encoding='utf-8') as file:
        json.dump(questions, file, indent=3, ensure_ascii=False)


if __name__ == "__main__":
    path = '/home/diana/calculator'
    adm_path = path + '/admin'

    os.chmod(path, 0o000)
    passw_len = 8       # длина пароля
    users_number = 5    # кол-во пользователей
    change_pass = 5     # время смены пароля
    auth_errors = 3     # кол-во допустимых ошибок при аутентификации

    if not os.path.exists(adm_path):
        os.mkdir(adm_path)

    if not os.path.exists(adm_path + '/journal.json'):
        create_journal()

    if not os.path.exists(adm_path + '/questions.json'):
        create_questions()

    app = QApplication(sys.argv)
    win = EnterWindow()
    win.show()
    app.exec_()
    os.chmod(path, 0o775)
    sys.exit()
