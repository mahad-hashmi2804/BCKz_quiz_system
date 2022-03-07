from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
from PyQt5 import *
from teacher_login import TeacherWindow
from student_login import StudentWindow
import mysql.connector
import time
import random
import datetime
from datetime import *
from PyQt5.Qt import QAbstractScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from operator import itemgetter
# from IPython.utils import strdispatch
from _ast import Pass
import sys
import pickle
import socket
import threading
from create_table_fpdf import PDF
import numpy

HEADER = 64
PORT = 5050
FORMAT = "utf-8"
DISCONNECT = "!DISCONNECT"
SERVER = "192.168.0.149"
# SERVER = "192.168.56.1"  # Laptop
# SERVER = "169.254.178.42"
# SERVER = "fe80::cd9e:6b06:39fc:b22a%16"  # PC - School
# SERVER = "fe80::34bd:266a:e6c6:78c8%12"  # Laptop - Home
ADDR = (SERVER, PORT)

LOGO = "Images/quiz_logo.jpg"
BC_LOGO = "Images/bckz_logo2.png"

# ADDR = (SERVER, PORT, 0, 0)


class Request:
    def __init__(self, kind, query, value):
        self.kind = kind
        self.value = value
        self.query = query


class ClickableLabel(QLabel):
    clicked = qtc.pyqtSignal()

    def mousePressEvent(self, ev):
        self.clicked.emit()


class Client:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)

    def send(self, msg):
        if type(msg) is str:
            msg = self.str_encode(msg)
        msg_length = len(msg)
        msg_length = str(msg_length).encode(FORMAT)
        msg_length += b' ' * (HEADER - len(msg_length))
        self.client.send(msg_length)
        self.client.send(msg)
        response = self.receive()
        # print(response)

    def str_encode(self, string):
        # print(pickle.dumps(string))
        return pickle.dumps(string)

    def disconnect(self):
        self.send(DISCONNECT)
        # print(DISCONNECT)
        # time.sleep(1)
        quit()

    def send_obj(self, obj):
        obj_send = pickle.dumps(obj)
        self.send(obj_send)

    def receive(self):
        msg_length = self.client.recv(HEADER).decode(FORMAT)
        msg_length = int(msg_length)
        # print(msg_length)
        msg = pickle.loads(self.client.recv(msg_length))
        return msg

    def query_sql(self, query, value):
        req = Request("SQL", query, value)
        self.send_obj(req)
        # print(query)
        if "SELECT" in req.query:
            number = self.receive()
            select = []
            for x in range(number):
                num = self.receive()
                tup = ()
                for y in range(num):
                    item = self.receive()
                    tup = tup + (item,)
                select.append(tup)
            # self.disconnect()
            return select


class answer:
    def setup(self, question_id, question, correct_answer, option_a, option_b, option_c, option_d, answer_select):
        self.question_id = question_id
        self.question = question
        self.correct_answer = correct_answer
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d
        self.answer_select = answer_select

    def correct(self, change):
        self.answer_select = change


class subject_score:
    def setup(self, name):
        subjects = {
            "Eng": "English",
            "Urdu": "Urdu",
            "Math": "Mathematics",
            "Phy": "Physics",
            "Chem": "Chemistry",
            "Bio": "Biology",
            "Isl": "Islamiyat",
            "P.St": "Pakistan Studies",
            "Comp": "Computer Science",
            "Add.Math": "Additional Mathematics"
        }

        self.name = name
        self.display_name = subjects.get(name)
        self.scores = []

    def add_score(self, correct, total, entry_date):
        score = (round(correct, 2), round(total, 2), entry_date)
        # print(score)
        self.scores.append(score)
        self.scores.sort(key=itemgetter(2), reverse=True)
        self.last_entry = self.scores[0]
        self.last_date = self.last_entry[2]
        self.last_date = self.last_date.strftime("%H:%M %a, %d %B %Y")

    def percentage(self):
        correct = 0
        total = 0
        for x in self.scores:
            correct += x[0]
            total += x[1]
        return (round(((correct / total) * 100), 2))


class Ui_MainWindow(object):
    client = Client()

    def setupStartup(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        # MainWindow.resize(1355, 700)
        # MainWindow.setStyleSheet("background-color: white;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # self.centralwidget.setStyleSheet("background-color: rgba(200,220,255,1)")
        self.logo_label = QtWidgets.QLabel(self.centralwidget)
        self.logo_label.setGeometry(QtCore.QRect(850, 10, 180, 180))
        self.logo_label.setText("")
        self.logo_label.setPixmap(QtGui.QPixmap(LOGO))
        self.logo_label.setScaledContents(True)
        font = QtGui.QFont()
        font.setFamily("Harrington")
        font.setPointSize(100)
        self.logo_label.setStyleSheet("color: #CC00FF;")
        self.logo_label.setFont(font)
        self.logo_label.setAlignment(QtCore.Qt.AlignCenter)
        self.logo_label.setIndent(0)
        self.logo_label.setObjectName("label")
        self.logo_label.setStyleSheet("background: transparent; border-radius: 30px;")
        self.horizontalWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalWidget.setGeometry(QtCore.QRect(0, 250, 1361, 410))
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setContentsMargins(240, 0, 240, 0)
        self.horizontalLayout.setSpacing(180)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.teacher_btn = QtWidgets.QPushButton(self.horizontalWidget)
        # self.teacher_btn.setStyleSheet("background-color: red;")
        self.teacher_btn.setMinimumSize(QtCore.QSize(350, 340))
        self.teacher_btn.setMaximumSize(QtCore.QSize(350, 340))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.teacher_btn.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/teacher.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.teacher_btn.setIcon(icon)
        self.teacher_btn.setIconSize(QtCore.QSize(150, 150))
        self.teacher_btn.setObjectName("teacher_btn")
        self.teacher_btn.clicked.connect(self.teacherLogin)
        self.horizontalLayout.addWidget(self.teacher_btn)
        self.student_btn = QtWidgets.QPushButton(self.horizontalWidget)
        self.student_btn.setMinimumSize(QtCore.QSize(350, 340))
        self.student_btn.setMaximumSize(QtCore.QSize(350, 340))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        font.setBold(False)
        font.setWeight(50)
        self.student_btn.setFont(font)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("Images/student.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.student_btn.setIcon(icon1)
        self.student_btn.setIconSize(QtCore.QSize(150, 150))
        self.student_btn.setObjectName("student_btn")
        self.student_btn.clicked.connect(self.studentLogin)
        self.horizontalLayout.addWidget(self.student_btn)
        self.question_label = QtWidgets.QLabel(self.centralwidget)
        self.question_label.setGeometry(QtCore.QRect(603, 160, 150, 71))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.question_label.setFont(font)
        self.question_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.question_label.setAlignment(QtCore.Qt.AlignCenter)
        self.question_label.setObjectName("question_label")
        self.question_label.setStyleSheet("border-radius: 10")

        self.logo2_label = QtWidgets.QLabel(self.centralwidget)
        self.logo2_label.setGeometry(QtCore.QRect(310, 10, 200, 200))
        self.logo2_label.setText("")
        self.logo2_label.setPixmap(QtGui.QPixmap(BC_LOGO))
        self.logo2_label.setScaledContents(True)
        font = QtGui.QFont()
        font.setFamily("Harrington")
        font.setPointSize(100)
        self.logo2_label.setStyleSheet('''QLabel{color: #CC00FF; background: rgba(255,255,255,0.7);
                                                  border: 10px solid;
                                                  border-image-slice: 1;
                                                  border-width: 5px;
                                                 border-radius: 50px;
                                                 border-image-source: linear-gradient(to left, #743ad5, #d53a9d);}''')
        self.logo2_label.setFont(font)
        self.logo2_label.setAlignment(QtCore.Qt.AlignCenter)
        self.logo2_label.setIndent(0)
        self.logo2_label.setObjectName("label")

        MainWindow.setCentralWidget(self.centralwidget)

        MainWindow.setWindowTitle("Quiz")
        self.teacher_btn.setText("Teacher")
        self.student_btn.setText("Student")
        self.question_label.setText("I am a: ")

        with open("style.css", "r") as s:
            MainWindow.setStyleSheet(s.read())
            pass

        self.SLogin = StudentWindow(self.client)
        self.TLogin = TeacherWindow(self.client)

        self.TLogin.success.connect(lambda: self.success_teacher_login(MainWindow))
        self.SLogin.success.connect(lambda: self.success_student_login(MainWindow))

        app.aboutToQuit.connect(self.client.disconnect)

    def teacherLogin(self):
        self.TLogin.close()
        self.TLogin.show()
        self.SLogin.close()

    def studentLogin(self):
        self.SLogin.close()
        self.SLogin.show()
        self.TLogin.close()

    def success_student_login(self, MainWindow):
        self.centralwidget.hide()
        name = self.SLogin.final_name
        self.name = name
        self.student_id = self.SLogin.student_id
        self.grade = self.SLogin.grade
        self.client.send(f"Student {name} logged in.")
        # print(name)
        self.setupStudentWindow(MainWindow)

    def success_teacher_login(self, MainWindow):
        self.centralwidget.hide()
        title = self.TLogin.username.currentText()
        compound = title.split(" - ")
        name = compound[0]
        self.name = name
        self.teacher_id = self.TLogin.username.currentData()
        self.client.send(f"Teacher {name} logged in.")
        self.setupTeacherWindow(MainWindow, name)

    def setupTeacherWindow(self, MainWindow, name):
        self.teacher_mainscreen = QtWidgets.QWidget(MainWindow)
        self.teacher_mainscreen.setObjectName("teacher_mainscreen")

        self.home_btn = QtWidgets.QPushButton(self.teacher_mainscreen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.hide()

        self.logout_btn = QtWidgets.QPushButton(self.teacher_mainscreen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.verticalWidget = QtWidgets.QWidget(self.teacher_mainscreen)
        self.verticalWidget.setGeometry(QtCore.QRect(0, 0, 1355, 700))
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        label = QtWidgets.QLabel(self.verticalWidget)
        label.setEnabled(True)
        label.setMinimumSize(QtCore.QSize(200, 200))
        label.setMaximumSize(QtCore.QSize(200, 200))
        label.setText("")
        label.setPixmap(QtGui.QPixmap(LOGO))
        label.setScaledContents(True)
        label.setObjectName("label")
        self.verticalLayout.addWidget(label, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.welcome_label = QtWidgets.QLabel(self.verticalWidget)
        self.welcome_label.setMinimumSize(QtCore.QSize(0, 65))
        self.welcome_label.setMaximumSize(QtCore.QSize(16777215, 1000))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.welcome_label.setFont(font)
        self.welcome_label.setScaledContents(False)
        self.welcome_label.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.welcome_label.setObjectName("welcome_label")
        self.verticalLayout.addWidget(self.welcome_label, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignCenter)

        select = self.client.query_sql("SELECT name FROM teachers WHERE teacher_id = %s", (self.teacher_id,))
        for x in select:
            self.teacher_name = x[0]
        self.welcome_label.setText(f"Welcome Back {self.teacher_name}!")

        self.horizontalWidget = QtWidgets.QWidget(self.verticalWidget)
        self.horizontalWidget.setMinimumSize(QtCore.QSize(1355, 190))
        self.horizontalWidget.setMaximumSize(QtCore.QSize(1355, 220))
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setContentsMargins(50, 1, 50, 5)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.manage_students_btn = QtWidgets.QPushButton(self.horizontalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.manage_students_btn.sizePolicy().hasHeightForWidth())
        self.manage_students_btn.setSizePolicy(sizePolicy)
        self.manage_students_btn.setMinimumSize(QtCore.QSize(600, 140))
        self.manage_students_btn.setMaximumSize(QtCore.QSize(600, 140))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.manage_students_btn.setFont(font)
        self.manage_students_btn.setObjectName("manage_students_btn")
        self.horizontalLayout.addWidget(self.manage_students_btn, 0, QtCore.Qt.AlignBottom)
        self.update_profile_btn = QtWidgets.QPushButton(self.horizontalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.update_profile_btn.sizePolicy().hasHeightForWidth())
        self.update_profile_btn.setSizePolicy(sizePolicy)
        self.update_profile_btn.setMinimumSize(QtCore.QSize(600, 140))
        self.update_profile_btn.setMaximumSize(QtCore.QSize(600, 140))

        self.update_profile_btn.setFont(font)
        self.update_profile_btn.setObjectName("update_profile_btn")
        self.horizontalLayout.addWidget(self.update_profile_btn, 0, QtCore.Qt.AlignBottom)
        self.verticalLayout.addWidget(self.horizontalWidget)
        self.horizontalWidget1 = QtWidgets.QWidget(self.verticalWidget)
        self.horizontalWidget1.setMinimumSize(QtCore.QSize(1355, 152))
        self.horizontalWidget1.setMaximumSize(QtCore.QSize(16777215, 200))
        self.horizontalWidget1.setObjectName("horizontalWidget1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalWidget1)
        self.horizontalLayout_2.setContentsMargins(50, 0, 50, 0)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.manage_questions_btn = QtWidgets.QPushButton(self.horizontalWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.manage_questions_btn.sizePolicy().hasHeightForWidth())
        self.manage_questions_btn.setSizePolicy(sizePolicy)
        self.manage_questions_btn.setMinimumSize(QtCore.QSize(600, 140))
        self.manage_questions_btn.setMaximumSize(QtCore.QSize(600, 140))

        self.manage_questions_btn.setFont(font)
        self.manage_questions_btn.setObjectName("manage_questions_btn")
        self.horizontalLayout_2.addWidget(self.manage_questions_btn, 0, QtCore.Qt.AlignBottom)
        self.create_student_btn = QtWidgets.QPushButton(self.horizontalWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.create_student_btn.sizePolicy().hasHeightForWidth())
        self.create_student_btn.setSizePolicy(sizePolicy)
        self.create_student_btn.setMinimumSize(QtCore.QSize(600, 140))
        self.create_student_btn.setMaximumSize(QtCore.QSize(600, 140))

        self.create_student_btn.setFont(font)
        self.create_student_btn.setObjectName("create_student_btn")
        self.horizontalLayout_2.addWidget(self.create_student_btn, 0, QtCore.Qt.AlignBottom)
        self.verticalLayout.addWidget(self.horizontalWidget1, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        MainWindow.setCentralWidget(self.teacher_mainscreen)

        MainWindow.setWindowTitle("Quiz - Teacher Window")
        self.manage_students_btn.setText("Manage Existing Students")
        self.update_profile_btn.setText("Update My Profile")
        self.manage_questions_btn.setText("Manage My Questions")
        self.create_student_btn.setText("Create a New Student User")

        self.update_error = None
        self.create_error = None
        self.create_msg = None

        info = self.client.query_sql("SELECT name, email, subject FROM teachers WHERE teacher_id = %s",
                                     (self.teacher_id,))
        for x in info:
            self.name = x[0]
            self.email = x[1]
            self.subject = x[2]

        self.manage_students_btn.clicked.connect(lambda: self.manage_students(MainWindow))
        self.update_profile_btn.clicked.connect(lambda: self.teacherUpdateProfile(MainWindow))
        self.manage_questions_btn.clicked.connect(lambda: self.manageQuestions(MainWindow))
        self.create_student_btn.clicked.connect(lambda: self.createStudent(MainWindow))
        app.aboutToQuit.connect(self.client.disconnect)
        self.logout_btn.raise_()

    # Teacher Sub-functions

    def teacher_home(self, MainWindow):
        self.home_btn.hide()
        self.setupTeacherWindow(MainWindow, self.teacher_name)

    def createStudent(self, MainWindow):
        self.create_student_screen = qtw.QWidget(MainWindow)
        self.create_student_screen.setObjectName("create_student_screen")

        self.home_btn = QtWidgets.QPushButton(self.create_student_screen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.create_student_screen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.verticalWidget = QtWidgets.QWidget(self.create_student_screen)
        self.verticalWidget.setGeometry(QtCore.QRect(0, 0, 1355, 700))
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(20, 10, 20, 20)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_6 = QtWidgets.QLabel(self.verticalWidget)
        self.label_6.setMaximumSize(QtCore.QSize(150, 150))
        self.label_6.setLineWidth(0)
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap(LOGO))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6, 0, QtCore.Qt.AlignHCenter)

        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)

        self.details_label = QtWidgets.QLabel(self.verticalWidget)
        self.details_label.setMinimumSize(QtCore.QSize(0, 0))
        self.details_label.setMaximumSize(QtCore.QSize(400, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.details_label.setFont(font)
        self.details_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.details_label.setObjectName("details_label")
        self.verticalLayout.addWidget(self.details_label)

        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)

        self.name_label = QtWidgets.QLabel(self.verticalWidget)
        self.name_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.name_label.setFont(font)
        self.name_label.setObjectName("name_label")
        self.verticalLayout.addWidget(self.name_label)

        self.nameEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.nameEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.nameEdit.setFont(font)
        self.nameEdit.setObjectName("nameEdit")
        self.verticalLayout.addWidget(self.nameEdit)

        spacerItem2 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)

        self.email_label = QtWidgets.QLabel(self.verticalWidget)
        self.email_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.email_label.setFont(font)
        self.email_label.setObjectName("email_label")
        self.verticalLayout.addWidget(self.email_label)

        self.emailEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.emailEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.emailEdit.setFont(font)
        self.emailEdit.setObjectName("emailEdit")
        self.verticalLayout.addWidget(self.emailEdit)

        spacerItem3 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem3)

        self.password_label = QtWidgets.QLabel(self.verticalWidget)
        self.password_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.verticalLayout.addWidget(self.password_label)

        self.passwordEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.passwordEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.passwordEdit.setFont(font)
        self.passwordEdit.setObjectName("passwordEdit")
        self.verticalLayout.addWidget(self.passwordEdit)

        spacerItem4 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem4)

        self.class_label = QtWidgets.QLabel(self.verticalWidget)
        self.class_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.class_label.setFont(font)
        self.class_label.setObjectName("class_label")
        self.verticalLayout.addWidget(self.class_label)

        self.classEdit = QtWidgets.QComboBox(self.verticalWidget)
        self.classEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.classEdit.setFont(font)
        self.classEdit.setObjectName("classEdit")
        self.verticalLayout.addWidget(self.classEdit)

        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem5)

        self.applyChanges_btn = QtWidgets.QPushButton(self.verticalWidget)
        self.applyChanges_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.applyChanges_btn.setObjectName("applyChanges_btn")
        self.applyChanges_btn.setFont(font)
        self.applyChanges_btn.clicked.connect(lambda: self.create_student(MainWindow))
        self.verticalLayout.addWidget(self.applyChanges_btn)

        MainWindow.setCentralWidget(self.create_student_screen)

        self.details_label.setText("Your Details:")
        self.name_label.setText("Name")
        self.email_label.setText("E-mail")
        self.password_label.setText("Password")
        self.class_label.setText("Class")
        self.applyChanges_btn.setText("Create Student")

        grades = [
            ("Junior 1 - A", "Jr1A"),
            ("Junior 1 - B", "Jr1B"),
            ("Junior 2 - A", "Jr2A"),
            ("Junior 2 - B", "Jr2B"),
            ("Senior 1 - A", "Sr1A"),
            ("Senior 1 - B", "Sr1B"),
            ("Senior 2 - A", "Sr2A"),
            ("Senior 2 - B", "Sr2B"),
            ("Senior 3 - A", "Sr3A"),
            ("Senior 3 - B", "Sr3B")
        ]

        self.details_label.setStyleSheet("")
        if self.create_error is not None:
            self.details_label.setText(self.create_error)
            self.details_label.setStyleSheet("color: white; background: #D50000; padding: 3px;")
        elif self.create_msg is not None:
            self.details_label.setText(self.create_msg)
            self.details_label.setStyleSheet("color: white; background: #64DD17; padding: 3px;")

        self.create_error = None

        for x in grades:
            self.classEdit.addItem(*x)

        self.home_btn.raise_()
        self.logout_btn.raise_()

        app.aboutToQuit.connect(self.client.disconnect)

    def create_student(self, MainWindow):
        name = self.nameEdit.text()
        email = self.emailEdit.text()
        password = self.passwordEdit.text()
        grade = self.classEdit.currentData()

        if len(name) == 0:
            self.create_error = "Name field can't be blank."
            self.createStudent(MainWindow)
        elif len(email) == 0:
            self.create_error = "Email field can't be blank."
            self.createStudent(MainWindow)
        elif "@" not in email:
            self.create_error = "Invalid Email."
            self.createStudent(MainWindow)
        elif len(password) == 0:
            self.create_error = "Password field can't be blank."
            self.createStudent(MainWindow)
        else:
            self.client.query_sql("INSERT INTO students (name, email, password, class) VALUES (%s, %s, %s, %s)", (name, email, password, grade))
            self.create_msg = "Profile Created"
            self.createStudent(MainWindow)

    def manageQuestions(self, MainWindow):
        self.manage_q_screen = QtWidgets.QWidget(MainWindow)
        self.manage_q_screen.setObjectName("manage_q_screen")

        self.home_btn = QtWidgets.QPushButton(self.manage_q_screen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.manage_q_screen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.logo_label = QtWidgets.QLabel(self.manage_q_screen)
        self.logo_label.setGeometry(QtCore.QRect(608, 10, 150, 150))
        self.logo_label.setText("")
        self.logo_label.setPixmap(QtGui.QPixmap(LOGO))
        self.logo_label.setScaledContents(True)
        self.logo_label.setObjectName("logo_label")
        self.q_func_btns = QtWidgets.QWidget(self.manage_q_screen)
        self.q_func_btns.setGeometry(QtCore.QRect(30, 620, 1301, 80))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.q_func_btns.setFont(font)
        self.q_func_btns.setObjectName("q_func_btns")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.q_func_btns)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.create_q_btn = QtWidgets.QPushButton(self.q_func_btns)
        self.create_q_btn.setMinimumSize(QtCore.QSize(300, 60))
        self.create_q_btn.setMaximumSize(QtCore.QSize(350, 16777215))
        self.create_q_btn.setObjectName("create_q_btn")
        self.horizontalLayout_2.addWidget(self.create_q_btn)
        self.edit_q_btn = QtWidgets.QPushButton(self.q_func_btns)
        self.edit_q_btn.setMinimumSize(QtCore.QSize(300, 60))
        self.edit_q_btn.setMaximumSize(QtCore.QSize(350, 16777215))
        self.edit_q_btn.setAutoRepeatDelay(310)
        self.edit_q_btn.setObjectName("edit_q_btn")
        self.horizontalLayout_2.addWidget(self.edit_q_btn)
        self.delete_q_btn = QtWidgets.QPushButton(self.q_func_btns)
        self.delete_q_btn.setMinimumSize(QtCore.QSize(300, 60))
        self.delete_q_btn.setMaximumSize(QtCore.QSize(350, 16777215))
        self.delete_q_btn.setObjectName("delete_q_btn")
        self.horizontalLayout_2.addWidget(self.delete_q_btn)
        self.q_display_table = QtWidgets.QTableWidget(self.manage_q_screen)
        self.q_display_table.setSortingEnabled(True)
        self.q_display_table.setGeometry(QtCore.QRect(60, 250, 1240, 350))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)
        self.q_display_table.setFont(font)
        self.q_display_table.setAlternatingRowColors(True)
        self.q_display_table.setObjectName("q_display_table")
        self.q_display_table.setColumnCount(6)

        item = QtWidgets.QTableWidgetItem()
        self.q_display_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_display_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_display_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_display_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_display_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.q_display_table.setHorizontalHeaderItem(5, item)
        self.q_display_table.horizontalHeader().setCascadingSectionResizes(True)
        self.q_display_table.setAlternatingRowColors(True)
        self.q_display_table.horizontalHeader().setDefaultSectionSize(99)
        self.q_display_table.verticalHeader().setDefaultSectionSize(80)
        self.q_display_table.setWordWrap(True)
        self.q_display_table.horizontalHeader().setSortIndicatorShown(True)
        self.q_display_table.horizontalHeader().setStretchLastSection(True)
        self.q_display_table.verticalHeader().setStretchLastSection(False)
        self.head_label2 = QtWidgets.QLabel(self.manage_q_screen)
        self.head_label2.setGeometry(QtCore.QRect(340, 180, 675, 50))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.head_label2.setFont(font)
        self.head_label2.setAlignment(QtCore.Qt.AlignCenter)
        self.head_label2.setWordWrap(True)
        self.head_label2.setObjectName("head_label2")
        MainWindow.setCentralWidget(self.manage_q_screen)

        MainWindow.setWindowTitle("Manage Questions")
        self.create_q_btn.setText("Create New Question")
        self.create_q_btn.setFont(font)
        self.create_q_btn.clicked.connect(lambda: self.createQuestion(MainWindow))
        self.edit_q_btn.setText("Edit Question")
        self.edit_q_btn.setFont(font)
        self.edit_q_btn.clicked.connect(lambda: self.editQuestion(MainWindow))
        self.edit_q_btn.setEnabled(False)
        self.delete_q_btn.setText("Delete Question")
        self.delete_q_btn.setFont(font)
        self.delete_q_btn.clicked.connect(lambda: self.deleteQuestion(MainWindow))
        self.delete_q_btn.setEnabled(False)

        item = self.q_display_table.horizontalHeaderItem(0)
        item.setText("Question")
        self.q_display_table.setColumnWidth(0, 300)
        item = self.q_display_table.horizontalHeaderItem(1)
        item.setText("Correct Answer")
        self.q_display_table.setColumnWidth(1, 200)
        item = self.q_display_table.horizontalHeaderItem(2)
        item.setText("Option A")
        self.q_display_table.setColumnWidth(2, 200)
        item = self.q_display_table.horizontalHeaderItem(3)
        item.setText("Option B")
        self.q_display_table.setColumnWidth(3, 200)
        item = self.q_display_table.horizontalHeaderItem(4)
        item.setText("Option C")
        self.q_display_table.setColumnWidth(4, 200)
        item = self.q_display_table.horizontalHeaderItem(5)
        item.setText("Class")
        self.head_label2.setText(
            "If you wish to edit or delete an existing question double-click the question the table below. "
            "If you wish to create a new question, click the button below.")

        self.questions = self.client.query_sql("SELECT question_id, question, answer, option_1, option_2, option_3, "
                                               "class FROM questions WHERE teacher = %s", (self.teacher_id,))

        self.q_display_table.setRowCount(len(self.questions))

        for num, q in enumerate(self.questions):
            item = qtw.QTableWidgetItem()
            self.q_display_table.setVerticalHeaderItem(num, item)
            item.setText(str(num + 1))

            question = qtw.QTableWidgetItem()
            self.q_display_table.setItem(num, 0, question)
            question.setText(str(q[1]))
            question.setFlags(Qt.ItemIsEnabled)

            c_answer = qtw.QTableWidgetItem()
            self.q_display_table.setItem(num, 1, c_answer)
            c_answer.setText(str(q[2]))
            c_answer.setFlags(Qt.ItemIsEnabled)

            answer_1 = qtw.QTableWidgetItem()
            self.q_display_table.setItem(num, 2, answer_1)
            answer_1.setText(str(q[3]))
            answer_1.setFlags(Qt.ItemIsEnabled)

            answer_2 = qtw.QTableWidgetItem()
            self.q_display_table.setItem(num, 3, answer_2)
            answer_2.setText(str(q[4]))
            answer_2.setFlags(Qt.ItemIsEnabled)

            answer_3 = qtw.QTableWidgetItem()
            self.q_display_table.setItem(num, 4, answer_3)
            answer_3.setText(str(q[5]))
            answer_3.setFlags(Qt.ItemIsEnabled)

            grade = qtw.QTableWidgetItem()
            self.q_display_table.setItem(num, 5, grade)
            grade.setText(str(q[6]))
            grade.setFlags(Qt.ItemIsEnabled)

        self.q_display_table.isEditable = False
        self.q_display_table.itemDoubleClicked.connect(self.q_select)
        self.q_display_table.itemClicked.connect(self.q_select)
        self.q_display_table.setSortingEnabled(True)

        self.create_msg = None

        self.logout_btn.raise_()
        self.home_btn.raise_()
        app.aboutToQuit.connect(self.client.disconnect)

    def q_select(self, q_obj):
        item = self.questions[q_obj.row()]
        self.selected_q_id = item[0]

        self.edit_q_btn.setEnabled(True)
        self.delete_q_btn.setEnabled(True)

    def editQuestion(self, MainWindow):
        self.edit_q_screen = QtWidgets.QWidget(MainWindow)
        self.edit_q_screen.setObjectName("edit_q_screen")

        self.home_btn = QtWidgets.QPushButton(self.edit_q_screen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.edit_q_screen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.verticalWidget = QtWidgets.QWidget(self.edit_q_screen)
        self.verticalWidget.setGeometry(QtCore.QRect(0, 0, 1355, 700))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        self.verticalWidget.setFont(font)
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(20, 10, 20, 20)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.logo_label = QtWidgets.QLabel(self.verticalWidget)
        self.logo_label.setMinimumSize(QtCore.QSize(150, 150))
        self.logo_label.setMaximumSize(QtCore.QSize(150, 150))
        self.logo_label.setLineWidth(0)
        self.logo_label.setText("")
        self.logo_label.setPixmap(QtGui.QPixmap(LOGO))
        self.logo_label.setScaledContents(True)
        self.logo_label.setObjectName("logo_label")
        self.verticalLayout.addWidget(self.logo_label, 0, QtCore.Qt.AlignHCenter)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.verticalWidget)
        self.label.setMinimumSize(QtCore.QSize(0, 0))
        self.label.setMaximumSize(QtCore.QSize(400, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label.setIndent(10)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(5, -1, -1, 3)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.label_2 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalWidget = QtWidgets.QWidget(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy)
        self.horizontalWidget.setMaximumSize(QtCore.QSize(16777215, 70))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.horizontalWidget.setFont(font)
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.q_text = QtWidgets.QPlainTextEdit(self.horizontalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.q_text.sizePolicy().hasHeightForWidth())

        self.q_text.setSizePolicy(sizePolicy)
        self.q_text.setMinimumSize(QtCore.QSize(645, 70))
        self.q_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.q_text.setObjectName("q_text")
        self.horizontalLayout.addWidget(self.q_text)
        self.c_ans_text = QtWidgets.QTextEdit(self.horizontalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.c_ans_text.sizePolicy().hasHeightForWidth())
        self.c_ans_text.setSizePolicy(sizePolicy)
        self.c_ans_text.setMinimumSize(QtCore.QSize(645, 0))
        self.c_ans_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.c_ans_text.setObjectName("c_ans_text")
        self.horizontalLayout.addWidget(self.c_ans_text)
        self.verticalLayout.addWidget(self.horizontalWidget)
        spacerItem2 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(5, -1, -1, -1)
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_8 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        self.label_7 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalWidget_2 = QtWidgets.QWidget(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget_2.sizePolicy().hasHeightForWidth())
        self.horizontalWidget_2.setSizePolicy(sizePolicy)
        self.horizontalWidget_2.setMaximumSize(QtCore.QSize(16777215, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.horizontalWidget_2.setFont(font)
        self.horizontalWidget_2.setObjectName("horizontalWidget_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalWidget_2)
        self.horizontalLayout_4.setContentsMargins(0, 3, 0, -1)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.ans_a_text = QtWidgets.QPlainTextEdit(self.horizontalWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ans_a_text.sizePolicy().hasHeightForWidth())
        self.ans_a_text.setSizePolicy(sizePolicy)
        self.ans_a_text.setMinimumSize(QtCore.QSize(645, 70))
        self.ans_a_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.ans_a_text.setObjectName("ans_a_text")
        self.horizontalLayout_4.addWidget(self.ans_a_text)
        self.ans_b_text = QtWidgets.QPlainTextEdit(self.horizontalWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ans_b_text.sizePolicy().hasHeightForWidth())
        self.ans_b_text.setSizePolicy(sizePolicy)
        self.ans_b_text.setMinimumSize(QtCore.QSize(645, 70))
        self.ans_b_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.ans_b_text.setObjectName("ans_b_text")
        self.horizontalLayout_4.addWidget(self.ans_b_text)
        self.verticalLayout.addWidget(self.horizontalWidget_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(5, -1, -1, -1)
        self.horizontalLayout_5.setSpacing(20)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_9 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_5.addWidget(self.label_9)
        self.label_10 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_5.addWidget(self.label_10)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalWidget_3 = QtWidgets.QWidget(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget_3.sizePolicy().hasHeightForWidth())
        self.horizontalWidget_3.setSizePolicy(sizePolicy)
        self.horizontalWidget_3.setMaximumSize(QtCore.QSize(16777215, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.horizontalWidget_3.setFont(font)
        self.horizontalWidget_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.horizontalWidget_3.setObjectName("horizontalWidget_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.horizontalWidget_3)
        self.horizontalLayout_6.setContentsMargins(0, 3, 0, -1)
        self.horizontalLayout_6.setSpacing(20)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.ans_c_text = QtWidgets.QPlainTextEdit(self.horizontalWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ans_c_text.sizePolicy().hasHeightForWidth())
        self.ans_c_text.setSizePolicy(sizePolicy)
        self.ans_c_text.setMinimumSize(QtCore.QSize(645, 70))
        self.ans_c_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.ans_c_text.setObjectName("ans_c_text")
        self.horizontalLayout_6.addWidget(self.ans_c_text)
        self.class_edit = QtWidgets.QComboBox(self.horizontalWidget_3)
        self.class_edit.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.class_edit.setFont(font)
        self.class_edit.setObjectName("class_edit")
        self.horizontalLayout_6.addWidget(self.class_edit)
        self.verticalLayout.addWidget(self.horizontalWidget_3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem4)
        self.h_widget = QtWidgets.QWidget(self.verticalWidget)
        self.h_widget.setObjectName("h_widget")
        self.h_layout = QtWidgets.QHBoxLayout(self.h_widget)
        self.h_layout.setContentsMargins(30, -1, 30, -1)
        self.h_layout.setSpacing(80)
        self.h_layout.setObjectName("h_layout")
        self.edit_q_btn = QtWidgets.QPushButton(self.h_widget)
        self.edit_q_btn.setMinimumSize(QtCore.QSize(0, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.edit_q_btn.setFont(font)
        self.edit_q_btn.setObjectName("create_q_btn")
        self.edit_q_btn.clicked.connect(lambda: self.edit_q(MainWindow))
        self.h_layout.addWidget(self.edit_q_btn)
        self.return_btn = QtWidgets.QPushButton(self.h_widget)
        self.return_btn.setMinimumSize(QtCore.QSize(0, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.return_btn.setFont(font)
        self.return_btn.setObjectName("return_btn")
        self.return_btn.clicked.connect(lambda: self.manageQuestions(MainWindow))
        self.h_layout.addWidget(self.return_btn)
        self.verticalLayout.addWidget(self.h_widget)
        MainWindow.setCentralWidget(self.edit_q_screen)

        self.label.setText("Edit the desired fields.")
        self.label_4.setText("Question")
        self.label_2.setText("Correct Answer")
        self.label_8.setText("Incorrect Option A")
        self.label_7.setText("Incorrect Option B")
        self.label_9.setText("Incorrect Option C")
        self.label_10.setText("Class")
        self.edit_q_btn.setText("Apply Changes")
        self.edit_q_btn.setEnabled(False)
        self.return_btn.setText("Back")

        text_font = QtGui.QFont()
        text_font.setFamily("Times New Roman")
        text_font.setPointSize(15)

        self.q_text.textChanged.connect(lambda: self.create_btn_ctrl(self.edit_q_btn))
        self.q_text.setPlaceholderText("Enter you question here")
        self.q_text.setFont(text_font)
        # self.q_text.setTextAlignment(Qt.AlignVBottom)
        self.c_ans_text.textChanged.connect(lambda: self.create_btn_ctrl(self.edit_q_btn))
        self.c_ans_text.setPlaceholderText("Enter the correct answer to this question")
        self.c_ans_text.setFont(text_font)
        self.ans_a_text.textChanged.connect(lambda: self.create_btn_ctrl(self.edit_q_btn))
        self.ans_a_text.setPlaceholderText("Enter an incorrect answer to go with this question")
        self.ans_a_text.setFont(text_font)
        self.ans_b_text.textChanged.connect(lambda: self.create_btn_ctrl(self.edit_q_btn))
        self.ans_b_text.setPlaceholderText("Enter an incorrect answer to go with this question")
        self.ans_b_text.setFont(text_font)
        self.ans_c_text.textChanged.connect(lambda: self.create_btn_ctrl(self.edit_q_btn))
        self.ans_c_text.setPlaceholderText("Enter an incorrect answer to go with this question")
        self.ans_c_text.setFont(text_font)

        q_obj = self.client.query_sql("SELECT question, answer, option_1, option_2, option_3, CLass FROM questions "
                                      "WHERE question_id = %s", (self.selected_q_id,))
        for x in q_obj:
            question = x[0]
            answer = x[1]
            op_a = x[2]
            op_b = x[3]
            op_c = x[4]
            grade = x[5]

        setup = [
            (self.q_text, question),
            (self.c_ans_text, answer),
            (self.ans_a_text, op_a),
            (self.ans_b_text, op_b),
            (self.ans_c_text, op_c),
        ]

        for x in setup:
            x[0].setPlainText(x[1])

        classes = [
            ("Junior 1 - A", "Jr1A"),
            ("Junior 1 - B", "Jr1B"),
            ("Junior 2 - A", "Jr2A"),
            ("Junior 2 - B", "Jr2B"),
            ("Senior 1 - A", "Sr1A"),
            ("Senior 1 - B", "Sr1B"),
            ("Senior 2 - A", "Sr2A"),
            ("Senior 2 - B", "Sr2B"),
            ("Senior 3 - A", "Sr3A"),
            ("Senior 3 - B", "Sr3B")
        ]

        for x in classes:
            self.class_edit.addItem(*x)
            if grade == x[1]:
                grade = x[0]
                # print(grade)

        self.class_edit.setCurrentText(grade)
        # print(grade)

        if self.create_msg is not None:
            self.label.setText(self.create_msg)
            self.label.setStyleSheet("color: white; background-color: #64DD17; border-radius: 5px; padding: 3px;")

        self.label.adjustSize()

        self.create_msg = None

        self.logout_btn.raise_()
        self.home_btn.raise_()
        app.aboutToQuit.connect(self.client.disconnect)

    def edit_q(self, MainWindow):
        question = self.q_text.toPlainText()
        answer = self.c_ans_text.toPlainText()
        op_a = self.ans_a_text.toPlainText()
        op_b = self.ans_b_text.toPlainText()
        op_c = self.ans_c_text.toPlainText()
        grade = self.class_edit.currentData()
        subject = self.subject
        q_id = self.selected_q_id

        self.client.query_sql("UPDATE questions SET question = %s, answer = %s, option_1 = %s, option_2 = %s, "
                              "option_3 = %s, subject = %s, Class = %s WHERE question_id = %s", (question, answer,
                                                                                                 op_a, op_b, op_c,
                                                                                                 subject, grade, q_id))

        self.create_msg = "Changes applied!"
        self.editQuestion(MainWindow)

    def deleteQuestion(self, MainWindow):
        self.delete_warning = qtw.QMessageBox()
        self.delete_warning.setWindowTitle("Delete Confirmation")
        self.delete_warning.setIcon(QMessageBox.Warning)
        # self.delete_warning.setTitle("Delete Confirmation")
        self.delete_warning.setText(f'''Are you sure you want to delete this question?
        This action can not be reversed.''')
        self.delete_warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = self.delete_warning.exec()
        if response == QMessageBox.Yes:
            self.client.query_sql("DELETE FROM questions WHERE question_id = %s", (self.selected_q_id,))
            self.manageQuestions(MainWindow)
        else:
            self.delete_warning.close()

    def createQuestion(self, MainWindow):
        self.create_q_screen = QtWidgets.QWidget(MainWindow)
        self.create_q_screen.setObjectName("create_q_screen")

        self.home_btn = QtWidgets.QPushButton(self.create_q_screen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.create_q_screen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.verticalWidget = QtWidgets.QWidget(self.create_q_screen)
        self.verticalWidget.setGeometry(QtCore.QRect(0, 0, 1355, 700))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        self.verticalWidget.setFont(font)
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(20, 10, 20, 20)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.logo_label = QtWidgets.QLabel(self.verticalWidget)
        self.logo_label.setMinimumSize(QtCore.QSize(150, 150))
        self.logo_label.setMaximumSize(QtCore.QSize(150, 150))
        self.logo_label.setLineWidth(0)
        self.logo_label.setText("")
        self.logo_label.setPixmap(QtGui.QPixmap(LOGO))
        self.logo_label.setScaledContents(True)
        self.logo_label.setObjectName("logo_label")
        self.verticalLayout.addWidget(self.logo_label, 0, QtCore.Qt.AlignHCenter)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.verticalWidget)
        self.label.setMinimumSize(QtCore.QSize(0, 0))
        self.label.setMaximumSize(QtCore.QSize(260, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label.setIndent(10)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(5, -1, -1, 3)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.label_2 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalWidget = QtWidgets.QWidget(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget.sizePolicy().hasHeightForWidth())
        self.horizontalWidget.setSizePolicy(sizePolicy)
        self.horizontalWidget.setMaximumSize(QtCore.QSize(16777215, 70))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.horizontalWidget.setFont(font)
        self.horizontalWidget.setObjectName("horizontalWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.q_text = QtWidgets.QPlainTextEdit(self.horizontalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.q_text.sizePolicy().hasHeightForWidth())

        self.q_text.setSizePolicy(sizePolicy)
        self.q_text.setMinimumSize(QtCore.QSize(645, 70))
        self.q_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.q_text.setObjectName("q_text")
        self.horizontalLayout.addWidget(self.q_text)
        self.c_ans_text = QtWidgets.QPlainTextEdit(self.horizontalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.c_ans_text.sizePolicy().hasHeightForWidth())
        self.c_ans_text.setSizePolicy(sizePolicy)
        self.c_ans_text.setMinimumSize(QtCore.QSize(645, 70))
        self.c_ans_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.c_ans_text.setObjectName("c_ans_text")
        self.horizontalLayout.addWidget(self.c_ans_text)
        self.verticalLayout.addWidget(self.horizontalWidget)
        spacerItem2 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(5, -1, -1, -1)
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_8 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        self.label_7 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalWidget_2 = QtWidgets.QWidget(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget_2.sizePolicy().hasHeightForWidth())
        self.horizontalWidget_2.setSizePolicy(sizePolicy)
        self.horizontalWidget_2.setMaximumSize(QtCore.QSize(16777215, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.horizontalWidget_2.setFont(font)
        self.horizontalWidget_2.setObjectName("horizontalWidget_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.horizontalWidget_2)
        self.horizontalLayout_4.setContentsMargins(0, 3, 0, -1)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.ans_a_text = QtWidgets.QPlainTextEdit(self.horizontalWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ans_a_text.sizePolicy().hasHeightForWidth())
        self.ans_a_text.setSizePolicy(sizePolicy)
        self.ans_a_text.setMinimumSize(QtCore.QSize(645, 70))
        self.ans_a_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.ans_a_text.setObjectName("ans_a_text")
        self.horizontalLayout_4.addWidget(self.ans_a_text)
        self.ans_b_text = QtWidgets.QPlainTextEdit(self.horizontalWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ans_b_text.sizePolicy().hasHeightForWidth())
        self.ans_b_text.setSizePolicy(sizePolicy)
        self.ans_b_text.setMinimumSize(QtCore.QSize(645, 70))
        self.ans_b_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.ans_b_text.setObjectName("ans_b_text")
        self.horizontalLayout_4.addWidget(self.ans_b_text)
        self.verticalLayout.addWidget(self.horizontalWidget_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(5, -1, -1, -1)
        self.horizontalLayout_5.setSpacing(20)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_9 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_5.addWidget(self.label_9)
        self.label_10 = QtWidgets.QLabel(self.verticalWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_5.addWidget(self.label_10)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalWidget_3 = QtWidgets.QWidget(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalWidget_3.sizePolicy().hasHeightForWidth())
        self.horizontalWidget_3.setSizePolicy(sizePolicy)
        self.horizontalWidget_3.setMaximumSize(QtCore.QSize(16777215, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.horizontalWidget_3.setFont(font)
        self.horizontalWidget_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.horizontalWidget_3.setObjectName("horizontalWidget_3")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.horizontalWidget_3)
        self.horizontalLayout_6.setContentsMargins(0, 3, 0, -1)
        self.horizontalLayout_6.setSpacing(20)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.ans_c_text = QtWidgets.QPlainTextEdit(self.horizontalWidget_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ans_c_text.sizePolicy().hasHeightForWidth())
        self.ans_c_text.setSizePolicy(sizePolicy)
        self.ans_c_text.setMinimumSize(QtCore.QSize(645, 70))
        self.ans_c_text.setMaximumSize(QtCore.QSize(16777215, 70))
        self.ans_c_text.setObjectName("ans_c_text")
        self.horizontalLayout_6.addWidget(self.ans_c_text)
        self.class_edit = QtWidgets.QComboBox(self.horizontalWidget_3)
        self.class_edit.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.class_edit.setFont(font)
        self.class_edit.setObjectName("class_edit")
        self.horizontalLayout_6.addWidget(self.class_edit)
        self.verticalLayout.addWidget(self.horizontalWidget_3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem4)
        self.h_widget = QtWidgets.QWidget(self.verticalWidget)
        self.h_widget.setObjectName("h_widget")
        self.h_layout = QtWidgets.QHBoxLayout(self.h_widget)
        self.h_layout.setContentsMargins(30, -1, 30, -1)
        self.h_layout.setSpacing(80)
        self.h_layout.setObjectName("h_layout")
        self.create_q_btn = QtWidgets.QPushButton(self.h_widget)
        self.create_q_btn.setMinimumSize(QtCore.QSize(0, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.create_q_btn.setFont(font)
        self.create_q_btn.setObjectName("create_q_btn")
        self.create_q_btn.clicked.connect(lambda: self.create_q(MainWindow))
        self.h_layout.addWidget(self.create_q_btn)
        self.return_btn = QtWidgets.QPushButton(self.h_widget)
        self.return_btn.setMinimumSize(QtCore.QSize(0, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.return_btn.setFont(font)
        self.return_btn.setObjectName("return_btn")
        self.return_btn.clicked.connect(lambda: self.manageQuestions(MainWindow))
        self.h_layout.addWidget(self.return_btn)
        self.verticalLayout.addWidget(self.h_widget)
        MainWindow.setCentralWidget(self.create_q_screen)

        self.label.setText("Fill in the details")
        self.label_4.setText("Question")
        self.label_2.setText("Correct Answer")
        self.label_8.setText("Incorrect Option A")
        self.label_7.setText("Incorrect Option B")
        self.label_9.setText("Incorrect Option C")
        self.label_10.setText("Class")
        self.create_q_btn.setText("Create Question")
        self.create_q_btn.setEnabled(False)
        self.return_btn.setText("Back")

        text_font = QtGui.QFont()
        text_font.setFamily("Times New Roman")
        text_font.setPointSize(15)

        self.q_text.textChanged.connect(lambda: self.create_btn_ctrl(self.create_q_btn))
        self.q_text.setPlaceholderText("Enter you question here")
        self.q_text.setFont(text_font)
        self.c_ans_text.textChanged.connect(lambda: self.create_btn_ctrl(self.create_q_btn))
        self.c_ans_text.setPlaceholderText("Enter the correct answer to this question")
        self.c_ans_text.setFont(text_font)
        self.ans_a_text.textChanged.connect(lambda: self.create_btn_ctrl(self.create_q_btn))
        self.ans_a_text.setPlaceholderText("Enter an incorrect answer to go with this question")
        self.ans_a_text.setFont(text_font)
        self.ans_b_text.textChanged.connect(lambda: self.create_btn_ctrl(self.create_q_btn))
        self.ans_b_text.setPlaceholderText("Enter an incorrect answer to go with this question")
        self.ans_b_text.setFont(text_font)
        self.ans_c_text.textChanged.connect(lambda: self.create_btn_ctrl(self.create_q_btn))
        self.ans_c_text.setPlaceholderText("Enter an incorrect answer to go with this question")
        self.ans_c_text.setFont(text_font)

        classes = [
            ("Junior 1 - A", "Jr1A"),
            ("Junior 1 - B", "Jr1B"),
            ("Junior 2 - A", "Jr2A"),
            ("Junior 2 - B", "Jr2B"),
            ("Senior 1 - A", "Sr1A"),
            ("Senior 1 - B", "Sr1B"),
            ("Senior 2 - A", "Sr2A"),
            ("Senior 2 - B", "Sr2B"),
            ("Senior 3 - A", "Sr3A"),
            ("Senior 3 - B", "Sr3B")
        ]

        for x in classes:
            self.class_edit.addItem(*x)

        if self.create_msg is not None:
            self.label.setText(self.create_msg)
            self.label.setStyleSheet("color: white; background-color: #64DD17; padding: 3px;")

            self.create_msg = None

        self.logout_btn.raise_()
        self.home_btn.raise_()
        app.aboutToQuit.connect(self.client.disconnect)

    def create_btn_ctrl(self, btn):
        fields = [
            self.q_text.toPlainText(),
            self.c_ans_text.toPlainText(),
            self.ans_a_text.toPlainText(),
            self.ans_b_text.toPlainText(),
            self.ans_c_text.toPlainText(),
        ]

        enabled = True

        for x in fields:
            # print(x)
            if len(x) == 0:
                enabled = False

        btn.setEnabled(enabled)

    def create_q(self, MainWindow):
        question = self.q_text.toPlainText()
        answer = self.c_ans_text.toPlainText()
        op_a = self.ans_a_text.toPlainText()
        op_b = self.ans_b_text.toPlainText()
        op_c = self.ans_c_text.toPlainText()
        grade = self.class_edit.currentData()
        subject = self.subject
        q_id = self.teacher_id

        self.client.query_sql("INSERT INTO questions (question, answer, option_1, option_2, option_3, subject, Class, "
                              "teacher) Values (%s, %s, %s, %s, %s, %s, %s, %s)", (question, answer, op_a, op_b,
                                                                                   op_c, subject, grade, q_id))

        self.create_msg = "Question created!"
        self.createQuestion(MainWindow)

    def teacherUpdateProfile(self, MainWindow):
        self.teacherUpdateScreen = QtWidgets.QWidget(MainWindow)
        self.teacherUpdateScreen.setObjectName("teacherUpdateScreen")

        self.home_btn = QtWidgets.QPushButton(self.teacherUpdateScreen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.teacherUpdateScreen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.verticalWidget = QtWidgets.QWidget(self.teacherUpdateScreen)
        self.verticalWidget.setGeometry(QtCore.QRect(0, 0, 1355, 700))
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(20, 10, 20, 20)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_6 = QtWidgets.QLabel(self.verticalWidget)
        self.label_6.setMaximumSize(QtCore.QSize(150, 150))
        self.label_6.setLineWidth(0)
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap(LOGO))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6, 0, QtCore.Qt.AlignHCenter)

        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)

        self.details_label = QtWidgets.QLabel(self.verticalWidget)
        self.details_label.setMinimumSize(QtCore.QSize(0, 0))
        self.details_label.setMaximumSize(QtCore.QSize(500, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.details_label.setFont(font)
        self.details_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.details_label.setObjectName("details_label")
        self.verticalLayout.addWidget(self.details_label)

        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)

        self.name_label = QtWidgets.QLabel(self.verticalWidget)
        self.name_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.name_label.setFont(font)
        self.name_label.setObjectName("name_label")
        self.verticalLayout.addWidget(self.name_label)

        self.nameEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.nameEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.nameEdit.setFont(font)
        self.nameEdit.setObjectName("nameEdit")
        self.verticalLayout.addWidget(self.nameEdit)

        spacerItem2 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)

        self.email_label = QtWidgets.QLabel(self.verticalWidget)
        self.email_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.email_label.setFont(font)
        self.email_label.setObjectName("email_label")
        self.verticalLayout.addWidget(self.email_label)

        self.emailEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.emailEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.emailEdit.setFont(font)
        self.emailEdit.setObjectName("emailEdit")
        self.verticalLayout.addWidget(self.emailEdit)

        spacerItem3 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem3)

        self.password_label = QtWidgets.QLabel(self.verticalWidget)
        self.password_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.verticalLayout.addWidget(self.password_label)

        self.passwordEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.passwordEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.passwordEdit.setFont(font)
        self.passwordEdit.setObjectName("passwordEdit")
        self.verticalLayout.addWidget(self.passwordEdit)

        spacerItem4 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem4)

        self.class_label = QtWidgets.QLabel(self.verticalWidget)
        self.class_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.class_label.setFont(font)
        self.class_label.setObjectName("class_label")
        self.verticalLayout.addWidget(self.class_label)

        self.classEdit = QtWidgets.QComboBox(self.verticalWidget)
        self.classEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.classEdit.setFont(font)
        self.classEdit.setObjectName("classEdit")
        self.verticalLayout.addWidget(self.classEdit)

        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem5)

        self.applyChanges_btn = QtWidgets.QPushButton(self.verticalWidget)
        self.applyChanges_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.applyChanges_btn.setObjectName("applyChanges_btn")
        self.applyChanges_btn.clicked.connect(lambda: self.applyTeacherChanges(MainWindow))
        self.verticalLayout.addWidget(self.applyChanges_btn)

        MainWindow.setCentralWidget(self.teacherUpdateScreen)

        self.details_label.setText("Your Details:")
        self.name_label.setText("Name")
        self.email_label.setText("E-mail")
        self.password_label.setText("Password")
        self.class_label.setText("Subject")
        self.applyChanges_btn.setText("Apply changes")

        subjects = [
            "Eng",
            "Urdu",
            "Phy",
            "Chem",
            "Bio",
            "Isl",
            "P.St",
            "Math",
            "Comp"
        ]

        teacher_id = self.teacher_id
        select = self.client.query_sql("SELECT * FROM teachers WHERE teacher_id = %s", (teacher_id,))
        for x in select:
            self.name = x[1]
            self.email = x[2]
            self.password = x[3]
            self.subject = x[4]

        self.nameEdit.setText(self.name)
        self.emailEdit.setText(self.email)
        self.passwordEdit.setText(self.password)
        self.classEdit.addItem(self.subject)

        subjects.remove(self.subject)
        for x in subjects:
            self.classEdit.addItem(x)

        self.details_label.setStyleSheet("")
        if self.update_error is not None:
            self.details_label.setText(self.update_error)
            self.details_label.setStyleSheet("color: white; background-color: #D50000; padding: 3px;")

        self.home_btn.raise_()
        self.logout_btn.raise_()

        self.update_error = None

        app.aboutToQuit.connect(self.client.disconnect)

    def applyTeacherChanges(self, MainWindow):
        name = self.nameEdit.text()
        email = self.emailEdit.text()
        password = self.passwordEdit.text()
        subject = self.classEdit.currentText()

        if len(name) == 0:
            self.update_error = "Name field can't be blank."
            self.teacherUpdateProfile(MainWindow)
        elif len(email) == 0:
            self.update_error = "Email field can't be blank."
            self.teacherUpdateProfile(MainWindow)
        elif "@" not in email:
            self.update_error = "Invalid Email."
            self.teacherUpdateProfile(MainWindow)
        elif len(password) == 0:
            self.update_error = "Password field can't be blank."
            self.teacherUpdateProfile(MainWindow)
        else:
            self.client.query_sql("UPDATE teachers SET name = %s, email = %s, password = %s, subject = %s WHERE "
                                  "teacher_id = %s", (name, email, password, subject, self.teacher_id))
            self.teacherUpdateProfile(MainWindow)

    def manage_students(self, MainWindow):
        self.manage_students_screen = QtWidgets.QWidget(MainWindow)
        self.manage_students_screen.setObjectName("manage_students_screen")

        self.home_btn = QtWidgets.QPushButton(self.manage_students_screen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.manage_students_screen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.logo_label = QtWidgets.QLabel(self.manage_students_screen)
        self.logo_label.setGeometry(QtCore.QRect(608, 10, 150, 150))
        self.logo_label.setText("")
        self.logo_label.setPixmap(QtGui.QPixmap(LOGO))
        self.logo_label.setScaledContents(True)
        self.logo_label.setObjectName("logo_label")
        self.manage_student_tab = QtWidgets.QTabWidget(self.manage_students_screen)
        self.manage_student_tab.setGeometry(QtCore.QRect(180, 205, 1000, 430))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.manage_student_tab.setFont(font)
        self.manage_student_tab.setStyleSheet("background-color: rgba(0,0,0,0)")
        self.manage_student_tab.setObjectName("manage_student_tab")
        self.name_page = QtWidgets.QWidget()
        self.name_page.setObjectName("name_page")
        self.name_entry = QtWidgets.QLineEdit(self.name_page)
        self.name_entry.setGeometry(QtCore.QRect(267, 15, 550, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.name_entry.setFont(font)
        self.name_entry.setObjectName("name_entry")
        self.name_entry.textEdited.connect(self.student_manage_refresh)
        self.used_label1 = QtWidgets.QLabel(self.name_page)
        self.used_label1.setGeometry(QtCore.QRect(50, 15, 210, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.used_label1.setFont(font)
        self.used_label1.setObjectName("used_label1")
        self.manage_student_tab.addTab(self.name_page, "")
        self.class_page = QtWidgets.QWidget()
        self.class_page.setObjectName("class_page")
        self.class_btn_layout = QtWidgets.QWidget(self.class_page)
        self.class_btn_layout.setGeometry(QtCore.QRect(0, 5, 1000, 50))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.class_btn_layout.setFont(font)
        self.class_btn_layout.setObjectName("class_btn_layout")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.class_btn_layout)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.jr1_btn = QtWidgets.QRadioButton(self.class_btn_layout)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.jr1_btn.setFont(font)
        self.jr1_btn.setObjectName("jr1_btn")
        self.horizontalLayout.addWidget(self.jr1_btn, 0, QtCore.Qt.AlignHCenter)
        self.jr2_btn = QtWidgets.QRadioButton(self.class_btn_layout)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.jr2_btn.setFont(font)
        self.jr2_btn.setObjectName("jr2_btn")
        self.horizontalLayout.addWidget(self.jr2_btn, 0, QtCore.Qt.AlignHCenter)
        self.sr1_btn = QtWidgets.QRadioButton(self.class_btn_layout)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.sr1_btn.setFont(font)
        self.sr1_btn.setObjectName("sr1_btn")
        self.horizontalLayout.addWidget(self.sr1_btn, 0, QtCore.Qt.AlignHCenter)
        self.sr2_btn = QtWidgets.QRadioButton(self.class_btn_layout)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.sr2_btn.setFont(font)
        self.sr2_btn.setObjectName("sr2_btn")
        self.horizontalLayout.addWidget(self.sr2_btn, 0, QtCore.Qt.AlignHCenter)
        self.sr3_btn = QtWidgets.QRadioButton(self.class_btn_layout)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.sr3_btn.setFont(font)
        self.sr3_btn.setObjectName("sr3_btn")
        self.horizontalLayout.addWidget(self.sr3_btn, 0, QtCore.Qt.AlignHCenter)
        self.manage_student_tab.addTab(self.class_page, "")
        self.std_func_btns = QtWidgets.QWidget(self.manage_students_screen)
        self.std_func_btns.setGeometry(QtCore.QRect(30, 630, 1300, 80))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.std_func_btns.setFont(font)
        self.std_func_btns.setObjectName("std_func_btns")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.std_func_btns)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.check_score_btn = QtWidgets.QPushButton(self.std_func_btns)
        self.check_score_btn.setMinimumSize(QtCore.QSize(350, 60))
        self.check_score_btn.setObjectName("check_score_btn")
        self.horizontalLayout_2.addWidget(self.check_score_btn, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.student_update_btn = QtWidgets.QPushButton(self.std_func_btns)
        self.student_update_btn.setMinimumSize(QtCore.QSize(350, 60))
        self.student_update_btn.setObjectName("student_update_btn")
        self.horizontalLayout_2.addWidget(self.student_update_btn, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.delete_student_btn = QtWidgets.QPushButton(self.std_func_btns)
        self.delete_student_btn.setMinimumSize(QtCore.QSize(350, 60))
        self.delete_student_btn.setMaximumSize(QtCore.QSize(205, 16777215))
        self.delete_student_btn.setObjectName("delete_student_btn")
        self.horizontalLayout_2.addWidget(self.delete_student_btn, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.student_display_table = QtWidgets.QTableWidget(self.manage_students_screen)
        self.student_display_table.setGeometry(QtCore.QRect(210, 290, 940, 330))
        self.student_display_table.setSortingEnabled(True)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(14)
        self.student_display_table.setFont(font)
        self.student_display_table.setAlternatingRowColors(True)
        self.student_display_table.setObjectName("student_display_table")
        self.student_display_table.setColumnCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.student_display_table.setHorizontalHeaderItem(0, item)
        self.student_display_table.setColumnWidth(1, 500)
        item = QtWidgets.QTableWidgetItem()
        self.student_display_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.student_display_table.setHorizontalHeaderItem(2, item)
        self.student_display_table.horizontalHeader().setSortIndicatorShown(True)
        self.student_display_table.horizontalHeader().setStretchLastSection(True)
        self.student_display_table.verticalHeader().setStretchLastSection(False)
        self.head_label1 = QtWidgets.QLabel(self.manage_students_screen)
        self.head_label1.setGeometry(QtCore.QRect(370, 165, 630, 35))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.head_label1.setFont(font)
        self.head_label1.setObjectName("head_label1")
        MainWindow.setCentralWidget(self.manage_students_screen)

        self.used_label1.setText("Enter the student\'s name:")
        self.manage_student_tab.setTabText(self.manage_student_tab.indexOf(self.name_page), ("Search by Name"))
        self.jr1_btn.setText("Junior 1")
        self.jr1_btn.clicked.connect(lambda: self.std_class_refresh("Jr1"))
        self.jr2_btn.setText("Junior 2")
        self.jr2_btn.clicked.connect(lambda: self.std_class_refresh("Jr2"))
        self.sr1_btn.setText("Senior 1")
        self.sr1_btn.clicked.connect(lambda: self.std_class_refresh("Sr1"))
        self.sr2_btn.setText("Senior 2")
        self.sr2_btn.clicked.connect(lambda: self.std_class_refresh("Sr2"))
        self.sr3_btn.setText("Senior 3")
        self.sr3_btn.clicked.connect(lambda: self.std_class_refresh("Sr3"))
        self.manage_student_tab.setTabText(self.manage_student_tab.indexOf(self.class_page), ("Search by Class"))
        self.check_score_btn.setText("View Student\'s Scores")
        self.check_score_btn.setEnabled(False)
        self.student_update_btn.setText("Update Student\'s Details")
        self.student_update_btn.setEnabled(False)
        self.delete_student_btn.setText("Delete Student\'s Profile")
        self.delete_student_btn.setEnabled(False)
        item = self.student_display_table.horizontalHeaderItem(0)
        item.setText("Student ID")
        item = self.student_display_table.horizontalHeaderItem(1)
        item.setText("Name")
        item = self.student_display_table.horizontalHeaderItem(2)
        item.setText("Class")
        self.head_label1.setText("Double-click the name of the student you wish to select in the table below.")

        self.students = self.client.query_sql("SELECT student_id, name, class FROM students", ())
        self.search = []

        self.student_display_table.setRowCount(len(self.students))

        for n, std in enumerate(self.students):
            item = qtw.QTableWidgetItem()
            self.student_display_table.setVerticalHeaderItem(n, item)
            item.setText(str(n + 1))

            id = qtw.QTableWidgetItem()
            self.student_display_table.setItem(n, 0, id)
            id.setText(str(std[0]))
            id.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            id.setFlags(qtc.Qt.ItemIsEnabled)

            name = qtw.QTableWidgetItem()
            self.student_display_table.setItem(n, 1, name)
            name.setText(std[1])
            name.setFlags(qtc.Qt.ItemIsEnabled)

            class_ = qtw.QTableWidgetItem()
            self.student_display_table.setItem(n, 2, class_)
            class_.setText(std[2])
            class_.setTextAlignment(Qt.AlignHCenter)
            class_.setFlags(qtc.Qt.ItemIsEnabled)
        self.student_display_table.isEditable = False
        self.student_display_table.itemDoubleClicked.connect(self.student_select)
        self.student_display_table.itemClicked.connect(self.student_select)

        self.student_update_btn.clicked.connect(lambda: self.std_update(MainWindow, self.selected_std_id))
        self.check_score_btn.clicked.connect(lambda: self.check_std_score(MainWindow, self.selected_std_id))
        self.delete_student_btn.clicked.connect(lambda: self.delete_std(MainWindow, self.selected_std_id))

        app.aboutToQuit.connect(self.client.disconnect)

    def student_select(self, std_object):
        student_index = std_object.row()
        if len(self.search) == 0:
            self.student_selection = self.students[student_index]
        else:
            self.student_selection = self.search[student_index]

        self.selected_std_id = self.student_selection[0]
        self.student_name = self.student_selection[1]
        student_class = self.student_selection[2]

        self.check_score_btn.setEnabled(True)
        self.student_update_btn.setEnabled(True)
        self.delete_student_btn.setEnabled(True)

    def delete_std(self, MainWindow, std_id):
        self.delete_warning = qtw.QMessageBox()
        self.delete_warning.setWindowTitle("Delete Confirmation")
        self.delete_warning.setIcon(QMessageBox.Warning)
        # self.delete_warning.setTitle("Delete Confirmation")
        name = self.client.query_sql("SELECT name FROM students WHERE student_id = %s", (std_id,))
        self.delete_warning.setText(f'''Are you sure you want to delete student profile '{''.join(name[0])}'?
All data corresponding with this profile will be lost permanently.''')
        self.delete_warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = self.delete_warning.exec()
        if response == QMessageBox.Yes:
            self.client.query_sql("DELETE FROM score WHERE student = %s", (std_id,))
            self.client.query_sql("DELETE FROM students WHERE student_id = %s", (std_id,))
            self.delete_warning.close()
            self.manage_students(MainWindow)
        else:
            self.delete_warning.close()

    def std_update(self, MainWindow, std_id):
        self.teacher_update_screen = QtWidgets.QWidget(MainWindow)
        self.teacher_update_screen.setObjectName("teacher_update_screen")

        self.home_btn = QtWidgets.QPushButton(self.teacher_update_screen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.teacher_update_screen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))

        self.verticalWidget = QtWidgets.QWidget(self.teacher_update_screen)
        self.verticalWidget.setGeometry(QtCore.QRect(0, 0, 1355, 700))
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(20, 10, 10, 20)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_6 = QtWidgets.QLabel(self.verticalWidget)
        self.label_6.setMaximumSize(QtCore.QSize(150, 150))
        self.label_6.setLineWidth(0)
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap(LOGO))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6, 0, QtCore.Qt.AlignHCenter)

        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)

        self.details_label = QtWidgets.QLabel(self.verticalWidget)
        self.details_label.setMinimumSize(QtCore.QSize(0, 0))
        self.details_label.setMaximumSize(QtCore.QSize(200, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.details_label.setFont(font)
        self.details_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.details_label.setObjectName("details_label")
        self.verticalLayout.addWidget(self.details_label)

        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)

        self.name_label = QtWidgets.QLabel(self.verticalWidget)
        self.name_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.name_label.setFont(font)
        self.name_label.setObjectName("name_label")
        self.verticalLayout.addWidget(self.name_label)

        self.nameEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.nameEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.nameEdit.setFont(font)
        self.nameEdit.setObjectName("nameEdit")
        self.verticalLayout.addWidget(self.nameEdit)

        spacerItem2 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)

        self.email_label = QtWidgets.QLabel(self.verticalWidget)
        self.email_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.email_label.setFont(font)
        self.email_label.setObjectName("email_label")
        self.verticalLayout.addWidget(self.email_label)

        self.emailEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.emailEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.emailEdit.setFont(font)
        self.emailEdit.setObjectName("emailEdit")
        self.verticalLayout.addWidget(self.emailEdit)

        spacerItem3 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem3)

        self.password_label = QtWidgets.QLabel(self.verticalWidget)
        self.password_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.verticalLayout.addWidget(self.password_label)

        self.passwordEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.passwordEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.passwordEdit.setFont(font)
        self.passwordEdit.setObjectName("passwordEdit")
        self.verticalLayout.addWidget(self.passwordEdit)

        spacerItem4 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem4)

        self.class_label = QtWidgets.QLabel(self.verticalWidget)
        self.class_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.class_label.setFont(font)
        self.class_label.setObjectName("class_label")
        self.verticalLayout.addWidget(self.class_label)

        self.classEdit = QtWidgets.QComboBox(self.verticalWidget)
        self.classEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.classEdit.setFont(font)
        self.classEdit.setObjectName("classEdit")
        self.verticalLayout.addWidget(self.classEdit)

        spacerItem5 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem5)

        self.h_widget = qtw.QWidget(self.verticalWidget)
        self.h_widget.setMinimumSize(QtCore.QSize(1315, 50))
        self.h_layout = qtw.QHBoxLayout(self.h_widget)
        self.h_layout.setSpacing(15)

        self.applyChanges_btn = QtWidgets.QPushButton(self.h_widget)
        self.applyChanges_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.applyChanges_btn.setFont(font)
        self.applyChanges_btn.setObjectName("applyChanges_btn")
        self.applyChanges_btn.clicked.connect(lambda: self.apply_student_changes(std_id))
        self.h_layout.addWidget(self.applyChanges_btn)

        self.return_btn = qtw.QPushButton()
        self.return_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.return_btn.setFont(font)
        self.return_btn.setObjectName("return_btn")
        self.return_btn.setText("Back")
        self.return_btn.clicked.connect(lambda: self.manage_students(MainWindow))
        self.h_layout.addWidget(self.return_btn)

        self.verticalLayout.addWidget(self.h_widget)

        MainWindow.setCentralWidget(self.teacher_update_screen)

        self.details_label.setText("Your Details:")
        self.name_label.setText("Name")
        self.email_label.setText("E-mail")
        self.password_label.setText("Password")
        self.class_label.setText("Class")
        self.applyChanges_btn.setText("Apply changes")

        grades = [
            ("Junior 1 - A", "Jr1A"),
            ("Junior 1 - B", "Jr1B"),
            ("Junior 2 - A", "Jr2A"),
            ("Junior 2 - B", "Jr2B"),
            ("Senior 1 - A", "Sr1A"),
            ("Senior 1 - B", "Sr1B"),
            ("Senior 2 - A", "Sr2A"),
            ("Senior 2 - B", "Sr2B"),
            ("Senior 3 - A", "Sr3A"),
            ("Senior 3 - B", "Sr3B")
        ]

        select = self.client.query_sql("SELECT * FROM students WHERE student_id = %s", (std_id,))
        for x in select:
            self.name = x[1]
            self.email = x[2]
            self.password = x[3]
            self.grade = x[4]

        self.nameEdit.setText(self.name)
        self.emailEdit.setText(self.email)
        self.passwordEdit.setText(self.password)
        # self.classEdit.addItem(self.grade)

        # grades.remove(self.grade)
        for x in grades:
            self.classEdit.addItem(*x)
            if x[1] == self.grade:
                self.classEdit.setCurrentText(x[0])

        self.home_btn.raise_()
        self.logout_btn.raise_()

        app.aboutToQuit.connect(self.client.disconnect)

    def check_std_score(self, MainWindow, student_id):
        self.teacher_score_view = QtWidgets.QWidget(MainWindow)
        self.teacher_score_view.setObjectName("teacher_score_view")

        self.home_btn = QtWidgets.QPushButton(self.teacher_score_view)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.teacher_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.teacher_score_view)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.return_btn = qtw.QPushButton(self.teacher_score_view)
        self.return_btn.setGeometry(QtCore.QRect(700, 640, 500, 50))
        self.return_btn.setObjectName("return_btn")
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.return_btn.setFont(font)
        self.return_btn.setText("Back")
        self.return_btn.clicked.connect(lambda: self.manage_students(MainWindow))

        self.create_rep_btn = qtw.QPushButton(self.teacher_score_view)
        self.create_rep_btn.setGeometry(QtCore.QRect(160, 640, 500, 50))
        self.create_rep_btn.setObjectName("create_rep_btn")
        self.create_rep_btn.setFont(font)
        self.create_rep_btn.setText("Create PDF Report")
        # self.create_rep_btn.clicked.connect()

        self.score_display = QtWidgets.QTableWidget(self.teacher_score_view)
        self.score_display.setEnabled(True)
        self.score_display.setSortingEnabled(True)
        self.score_display.setGeometry(QtCore.QRect(30, 245, 1301, 380))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.score_display.setFont(font)
        self.score_display.setAlternatingRowColors(True)
        self.score_display.setGridStyle(QtCore.Qt.SolidLine)
        self.score_display.setCornerButtonEnabled(True)
        self.score_display.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.score_display.setObjectName("score_display")
        self.score_display.setColumnCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(0, item)
        self.score_display.setColumnWidth(0, 300)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(1, item)
        self.score_display.setColumnWidth(1, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(2, item)
        self.score_display.setColumnWidth(2, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(3, item)
        self.score_display.setColumnWidth(3, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(4, item)
        self.score_display.horizontalHeader().setStretchLastSection(True)
        # self.score_display.horizontalHeader().setDefaultSectionSize(256)
        self.logo_label = QtWidgets.QLabel(self.teacher_score_view)
        self.logo_label.setGeometry(QtCore.QRect(608, 10, 150, 150))
        self.logo_label.setText("")
        self.logo_label.setPixmap(QtGui.QPixmap(LOGO))
        self.logo_label.setScaledContents(True)
        self.logo_label.setObjectName("logo_label")
        self.label = QtWidgets.QLabel(self.teacher_score_view)
        self.label.setGeometry(QtCore.QRect(35, 175, 1280, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.back_btn = QPushButton(self.teacher_score_view)
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setGeometry(QtCore.QRect(10, 10, 55, 55))
        # self.back_btn.setText("Go Back")
        self.back_btn.clicked.connect(lambda: self.check_std_score(MainWindow, student_id))
        back_icon = QtGui.QIcon()
        back_icon.addPixmap(QtGui.QPixmap("Images/return.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.back_btn.setIcon(back_icon)
        self.back_btn.setIconSize(QtCore.QSize(45, 45))
        self.back_btn.hide()
        MainWindow.setCentralWidget(self.teacher_score_view)

        item = self.score_display.horizontalHeaderItem(0)
        item.setText("Subject")
        item = self.score_display.horizontalHeaderItem(1)
        item.setText("Correct Answers")
        item = self.score_display.horizontalHeaderItem(2)
        item.setText("Total Answers")
        item = self.score_display.horizontalHeaderItem(3)
        item.setText("Percentage")
        item = self.score_display.horizontalHeaderItem(4)
        item.setText("Last Updated")
        self.label.setText(f'''{self.student_name}'s Scores
        Double-click a subject for its complete score history.''')

        self.subjects = []
        select = self.client.query_sql(
            "SELECT student, subject, date_of_entry, correct_answers, total_answers FROM score WHERE student = %s",
            (student_id,))
        for x in select:
            # print(x)
            if len(self.subjects) == 0:
                score = subject_score()
                score.setup(x[1])
                score.add_score(x[3], x[4], x[2])
                self.subjects.append(score)
                # print(subjects)

            else:
                inlist = False
                for y in self.subjects:
                    if x[1] == y.name:
                        inlist = True
                        subject = y
                        break

                if inlist == True:
                    subject.add_score(x[3], x[4], x[2])
                    # print(subjects)

                else:
                    score = subject_score()
                    score.setup(x[1])
                    self.subjects.append(score)
                    score.add_score(x[3], x[4], x[2])
                    # print(subjects)
        # print(self.subjects)

        self.create_rep_btn.clicked.connect(lambda: self.create_report(student_id, self.subjects))

        self.score_display.setRowCount(len(self.subjects))
        # print(len(subjects))

        if len(self.subjects) == 0:
            self.label.setText("This student has not attempted any quizzes.")

        for number, obj in enumerate(self.subjects):
            # number = x[0]
            # object = x[1]
            correct = 0
            total = 0

            entry = qtw.QTableWidgetItem()
            self.score_display.setVerticalHeaderItem(number, entry)
            entry.setText(str(number + 1))

            subject = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 0, subject)
            subject.setText(obj.display_name)
            subject.setFlags(qtc.Qt.ItemIsEnabled)
            subject.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            scored = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 1, scored)
            for y in obj.scores:
                correct += y[0]
                total += y[1]
            scored.setText(str(correct))
            scored.setFlags(qtc.Qt.ItemIsEnabled)
            scored.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            total_answered = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 2, total_answered)
            total_answered.setText(str(total))
            total_answered.setFlags(qtc.Qt.ItemIsEnabled)
            total_answered.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            percentage = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 3, percentage)
            percentage.setText(f"{obj.percentage()}%")
            percentage.setFlags(qtc.Qt.ItemIsEnabled)
            percentage.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            date = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 4, date)
            date.setText(f"{obj.last_date}")
            date.setFlags(qtc.Qt.ItemIsEnabled)
            date.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            # print(f"{obj.display_name}, {correct}, {total}, {obj.percentage()}%, {obj.last_date}")

        self.score_display.isEditable = False
        self.score_history_disable = False
        self.score_display.itemDoubleClicked.connect(lambda x: self.score_history(x))
        self.score_display.itemClicked.connect(lambda x: self.score_history(x))

        app.aboutToQuit.connect(self.client.disconnect)

    def std_class_refresh(self, grade):
        self.search = [i for i in self.students if grade in i[2]]

        self.student_display_table.setRowCount(len(self.search))

        for n, std in enumerate(self.search):
            item = qtw.QTableWidgetItem()
            self.student_display_table.setVerticalHeaderItem(n, item)
            item.setText(str(n + 1))

            id = qtw.QTableWidgetItem()
            self.student_display_table.setItem(n, 0, id)
            id.setText(str(std[0]))
            id.setTextAlignment(Qt.AlignRight)
            id.setFlags(qtc.Qt.ItemIsEnabled)

            name = qtw.QTableWidgetItem()
            self.student_display_table.setItem(n, 1, name)
            name.setText(std[1])
            name.setFlags(qtc.Qt.ItemIsEnabled)

            class_ = qtw.QTableWidgetItem()
            self.student_display_table.setItem(n, 2, class_)
            class_.setText(std[2])
            class_.setFlags(qtc.Qt.ItemIsEnabled)
            class_.setTextAlignment(Qt.AlignHCenter)

    def student_manage_refresh(self, name):
        # print(name)
        self.student_display_table.clear()

        item = qtw.QTableWidgetItem()
        item.setText("Student ID")
        self.student_display_table.setHorizontalHeaderItem(0, item)

        item = qtw.QTableWidgetItem()
        item.setText("Student Name")
        self.student_display_table.setHorizontalHeaderItem(1, item)

        item = qtw.QTableWidgetItem()
        item.setText("Class")
        self.student_display_table.setHorizontalHeaderItem(2, item)

        if len(name) == 0:
            self.student_display_table.setRowCount(len(self.students))
            self.search = []

            for n, std in enumerate(self.students):
                item = qtw.QTableWidgetItem()
                self.student_display_table.setVerticalHeaderItem(n, item)
                item.setText(str(n + 1))

                id = qtw.QTableWidgetItem()
                self.student_display_table.setItem(n, 0, id)
                id.setText(str(std[0]))
                id.setTextAlignment(Qt.AlignRight)
                id.setFlags(qtc.Qt.ItemIsEnabled)

                name = qtw.QTableWidgetItem()
                self.student_display_table.setItem(n, 1, name)
                name.setText(std[1])
                name.setFlags(qtc.Qt.ItemIsEnabled)

                class_ = qtw.QTableWidgetItem()
                self.student_display_table.setItem(n, 2, class_)
                class_.setText(std[2])
                class_.setTextAlignment(Qt.AlignHCenter)
                class_.setFlags(qtc.Qt.ItemIsEnabled)

        else:
            self.search = [i for i in self.students if name.lower() in i[1].lower()]
            # self.student_display_table.clear()

            self.student_display_table.setRowCount(len(self.search))

            for n, std in enumerate(self.search):
                item = qtw.QTableWidgetItem()
                self.student_display_table.setVerticalHeaderItem(n, item)
                item.setText(str(n + 1))

                id = qtw.QTableWidgetItem()
                self.student_display_table.setItem(n, 0, id)
                id.setText(str(std[0]))
                id.setTextAlignment(Qt.AlignRight)
                id.setFlags(qtc.Qt.ItemIsEnabled)

                name = qtw.QTableWidgetItem()
                self.student_display_table.setItem(n, 1, name)
                name.setText(std[1])
                name.setFlags(qtc.Qt.ItemIsEnabled)

                class_ = qtw.QTableWidgetItem()
                self.student_display_table.setItem(n, 2, class_)
                class_.setText(std[2])
                class_.setTextAlignment(Qt.AlignHCenter)
                class_.setFlags(qtc.Qt.ItemIsEnabled)

    def setupStudentWindow(self, MainWindow):  # Student Main Window
        self.student_mainscreen = QtWidgets.QWidget(MainWindow)
        self.student_mainscreen.setObjectName("student_mainscreen")

        self.home_btn = QtWidgets.QPushButton(self.student_mainscreen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.hide()

        self.logout_btn = QtWidgets.QPushButton(self.student_mainscreen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.verticalWidget = QtWidgets.QWidget(self.student_mainscreen)
        self.verticalWidget.setGeometry(QtCore.QRect(0, 0, 1355, 700))
        self.verticalWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(0, 10, 0, 10)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")

        logo = QtWidgets.QLabel(self.verticalWidget)
        logo.setEnabled(True)
        logo.setMinimumSize(QtCore.QSize(200, 200))
        logo.setMaximumSize(QtCore.QSize(200, 200))
        logo.setText("")
        logo.setPixmap(QtGui.QPixmap(LOGO))
        logo.setScaledContents(True)
        logo.setObjectName("logo")
        self.verticalLayout.addWidget(logo, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.welcome_label = QtWidgets.QLabel(self.verticalWidget)
        self.welcome_label.setMinimumSize(QtCore.QSize(0, 65))
        self.welcome_label.setMaximumSize(QtCore.QSize(16777215, 1000))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.welcome_label.setFont(font)
        self.welcome_label.setScaledContents(False)
        self.welcome_label.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter)
        self.welcome_label.setObjectName("welcome_label")
        self.verticalLayout.addWidget(self.welcome_label, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.quiz_btn = QtWidgets.QPushButton(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.quiz_btn.sizePolicy().hasHeightForWidth())
        self.quiz_btn.setSizePolicy(sizePolicy)
        self.quiz_btn.setMinimumSize(QtCore.QSize(1000, 100))
        self.quiz_btn.setMaximumSize(QtCore.QSize(1000, 100))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.quiz_btn.setFont(font)
        self.quiz_btn.setObjectName("quiz_btn")
        self.verticalLayout.addWidget(self.quiz_btn, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.updateProfile = QtWidgets.QPushButton(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.updateProfile.sizePolicy().hasHeightForWidth())
        self.updateProfile.setSizePolicy(sizePolicy)
        self.updateProfile.setMinimumSize(QtCore.QSize(1000, 100))
        self.updateProfile.setMaximumSize(QtCore.QSize(1000, 100))
        self.updateProfile.setFont(font)
        self.updateProfile.setObjectName("updateProfile")
        self.verticalLayout.addWidget(self.updateProfile, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.updateProfile.clicked.connect(lambda: self.studentUpdateProfile(StartupWindow))

        self.viewScore = QtWidgets.QPushButton(self.verticalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewScore.sizePolicy().hasHeightForWidth())
        self.viewScore.setSizePolicy(sizePolicy)
        self.viewScore.setMinimumSize(QtCore.QSize(1000, 100))
        self.viewScore.setMaximumSize(QtCore.QSize(1000, 100))
        self.viewScore.clicked.connect(lambda: self.studentViewScore(MainWindow))

        self.viewScore.setFont(font)
        self.viewScore.setObjectName("viewScore")
        self.verticalLayout.addWidget(self.viewScore, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        MainWindow.setCentralWidget(self.student_mainscreen)

        MainWindow.setWindowTitle("MainWindow")
        self.welcome_label.setText("Welcome Back !")
        self.quiz_btn.setText("Start Quiz")
        self.quiz_btn.clicked.connect(self.student_quiz_btn)
        self.updateProfile.setText("Update My Profile")
        self.viewScore.setText("View My Score")
        std_id = self.student_id
        select = self.client.query_sql("SELECT name FROM students WHERE student_id = %s", (std_id,))
        for x in select:
            self.name = x[0]
        self.welcome_label.setText(f"Welcome Back {self.name}!")

        self.logout_btn.raise_()

        app.aboutToQuit.connect(self.client.disconnect)

    # Student Sub-functions

    def student_home(self, MainWindow):
        self.home_btn.hide()
        self.setupStudentWindow(MainWindow)

    def logout(self, MainWindow):
        self.home_btn.hide()
        self.logout_btn.hide()
        self.setupStartup(MainWindow)
        self.client.send(f"{self.name} logged out")

    def student_quiz_btn(self):
        self.student_mainscreen.hide()
        self.setupQuiz(StartupWindow)

    def setupQuiz(self, MainWindow):  # Quiz Setup
        self.history = []

        self.check_clicked = False

        self.QuizWindow = QtWidgets.QWidget(MainWindow)
        self.QuizWindow.setObjectName("QuizWindow")

        self.home_btn = QtWidgets.QPushButton(self.QuizWindow)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.QuizWindow)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))

        self.gridWidget = QtWidgets.QWidget(self.QuizWindow)
        self.gridWidget.setGeometry(QtCore.QRect(0, 300, 1355, 281))
        self.gridWidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Pakistan))
        self.gridWidget.setObjectName("gridWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setContentsMargins(40, 30, 0, 0)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.option_b = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_b.setFont(font)
        self.option_b.setObjectName("option_b")
        self.gridLayout.addWidget(self.option_b, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_c_label = ClickableLabel(self.gridWidget)
        self.option_c_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_c_label.setFont(font)
        self.option_c_label.setWordWrap(True)
        self.option_c_label.setObjectName("option_c_label")
        self.gridLayout.addWidget(self.option_c_label, 0, 3, 1, 1, QtCore.Qt.AlignLeft)
        self.option_a_label = ClickableLabel(self.gridWidget)
        self.option_a_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_a_label.setFont(font)
        self.option_a_label.setAutoFillBackground(False)
        self.option_a_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.option_a_label.setWordWrap(True)
        self.option_a_label.setObjectName("option_a_label")
        self.gridLayout.addWidget(self.option_a_label, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.option_d = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_d.setFont(font)
        self.option_d.setObjectName("option_d")
        self.gridLayout.addWidget(self.option_d, 2, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_b_label = ClickableLabel(self.gridWidget)
        self.option_b_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_b_label.setFont(font)
        self.option_b_label.setWordWrap(True)
        self.option_b_label.setObjectName("option_b_label")
        self.gridLayout.addWidget(self.option_b_label, 2, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.option_c = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_c.setFont(font)
        self.option_c.setObjectName("option_c")
        self.gridLayout.addWidget(self.option_c, 0, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_a = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_a.setFont(font)
        self.option_a.setObjectName("option_a")
        self.gridLayout.addWidget(self.option_a, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_d_label = ClickableLabel(self.gridWidget)
        self.option_d_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_d_label.setFont(font)
        self.option_d_label.setWordWrap(True)
        self.option_d_label.setObjectName("option_d_label")
        self.gridLayout.addWidget(self.option_d_label, 2, 3, 1, 1, QtCore.Qt.AlignLeft)
        self.gridLayout.setColumnMinimumWidth(0, 40)
        self.gridLayout.setColumnMinimumWidth(1, 650)
        self.gridLayout.setColumnMinimumWidth(2, 40)
        self.gridLayout.setColumnMinimumWidth(3, 650)
        self.gridLayout.setRowMinimumHeight(0, 75)
        self.gridLayout.setRowMinimumHeight(1, 75)
        self.gridLayout.setColumnStretch(0, 20)
        self.gridLayout.setColumnStretch(1, 500)
        self.gridLayout.setColumnStretch(2, 20)
        self.gridLayout.setColumnStretch(3, 500)
        self.gridLayout.setRowStretch(0, 75)
        self.gridLayout.setRowStretch(2, 75)
        self.logo = QtWidgets.QLabel(self.QuizWindow)
        self.logo.setGeometry(QtCore.QRect(582, 30, 200, 200))
        self.logo.setMinimumSize(QtCore.QSize(150, 150))
        self.logo.setMaximumSize(QtCore.QSize(200, 200))
        self.logo.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Pakistan))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap(LOGO))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")

        self.submit_btn = QtWidgets.QPushButton(self.QuizWindow)
        self.submit_btn.setGeometry(QtCore.QRect(370, 600, 290, 60))
        # self.submit_btn.setMinimumSize(QtCore.QSize(600, 60))
        # self.submit_btn.setMaximumSize(QtCore.QSize(600, 16777215))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(22)
        self.submit_btn.setFont(font)
        self.submit_btn.setObjectName("submit_btn")
        self.submit_btn.clicked.connect(self.submit_final_answer)

        self.question_display = QtWidgets.QTextEdit(self.QuizWindow)
        self.question_display.setGeometry(QtCore.QRect(126, 210, 1100, 100))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.question_display.setFont(font)
        self.question_display.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.question_display.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.question_display.setObjectName("question_display")
        self.question_display.setStyleSheet("background-color: rgba(236,239,241,0.7)")
        self.question_display.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

        self.select_btn = QtWidgets.QPushButton(self.QuizWindow)
        self.select_btn.setGeometry(QtCore.QRect(580, 480, 200, 60))
        self.select_btn.setMinimumSize(QtCore.QSize(0, 0))
        self.select_btn.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(22)
        self.select_btn.setFont(font)
        self.select_btn.setObjectName("select_btn")

        self.subject_combo = QtWidgets.QComboBox(self.QuizWindow)
        self.subject_combo.setGeometry(QtCore.QRect(565, 360, 230, 51))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.subject_combo.setFont(font)
        self.subject_combo.setObjectName("subject_combo")

        self.label = QtWidgets.QLabel(self.QuizWindow)
        self.label.setGeometry(QtCore.QRect(520, 275, 330, 50))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setObjectName("label")

        MainWindow.setCentralWidget(self.QuizWindow)

        MainWindow.setWindowTitle("Quiz")
        self.option_b.setText("B:")
        self.option_c.setText("C:")
        self.option_d.setText("D:")
        self.option_a.setText("A:")
        self.submit_btn.setText("Submit")
        self.question_display.setText("")

        self.label.setText("Pick your desired subject:")
        self.select_btn.setText("Select")

        self.finalize_btn = QtWidgets.QPushButton(self.QuizWindow)
        self.finalize_btn.setObjectName("finalize_btn")
        self.finalize_btn.setGeometry(QtCore.QRect(680, 600, 290, 60))
        self.finalize_btn.setFont(font)
        self.finalize_btn.setText("End Quiz")
        self.finalize_btn.hide()
        self.finalize_btn.clicked.connect(lambda: self.answer_confirm(MainWindow))
        self.finalize_btn.setEnabled(False)

        self.question_count = QtWidgets.QLCDNumber(self.QuizWindow)
        self.question_count.setGeometry(QtCore.QRect(1130, 70, 100, 50))
        self.question_count.setObjectName("question_count")

        self.label_3 = QtWidgets.QLabel(self.QuizWindow)  # working here
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QtCore.QRect(900, 78, 220, 40))
        self.label_3.setText("No. of questions answered")
        font.setPointSize(16)
        self.label_3.setFont(font)

        subjects = [
            ("English", "Eng"),
            ("Urdu", "Urdu"),
            ("Math", "Math"),
            ("Physics", "Phy"),
            ("Chemistry", "Chem"),
            ("Biology", "Bio"),
            ("Islamiyat", "Isl"),
            ("Pakistan Studies", "P.St"),
            ("Computer Science", "Comp"),
            ("Additional Maths", "Add.Math")
        ]

        for x in subjects:
            self.subject_combo.addItem(x[0], x[1])

        self.option_group = QtWidgets.QButtonGroup(self.QuizWindow)
        self.option_group.addButton(self.option_a)
        self.option_group.addButton(self.option_b)
        self.option_group.addButton(self.option_c)
        self.option_group.addButton(self.option_d)

        self.question_display.hide()
        self.submit_btn.hide()
        self.option_a.hide()
        self.option_a_label.hide()
        self.option_b.hide()
        self.option_b_label.hide()
        self.option_c.hide()
        self.option_c_label.hide()
        self.option_d.hide()
        self.option_d_label.hide()
        self.question_count.hide()
        self.label_3.hide()

        self.select_btn.clicked.connect(lambda: self.selected_subject(self.subject_combo.currentData()))
        app.aboutToQuit.connect(self.client.disconnect)

    def selected_subject(self, subject):  # Quiz Sub-function
        self.subject_select = subject

        self.questions = self.client.query_sql(
            f"SELECT * FROM questions WHERE subject = '{self.subject_select}' AND class = '{self.grade}'", ())
        # print(self.questions)
        # return

        self.select_btn.hide()
        self.subject_combo.hide()
        self.label.hide()

        self.logo.setGeometry(QtCore.QRect(595, 10, 180, 180))

        self.question_display.show()
        self.submit_btn.show()
        self.option_a.show()
        self.option_a_label.show()
        self.option_b.show()
        self.option_b_label.show()
        self.option_c.show()
        self.option_c_label.show()
        self.option_d.show()
        self.option_d_label.show()
        self.question_count.show()
        self.label_3.show()
        self.finalize_btn.show()

        self.quiz()
        app.aboutToQuit.connect(self.client.disconnect)

    def quiz(self):  # Quiz Sub-function
        if len(self.questions) == 0:
            self.question_display.setText("You have answered all questions for the current class and subject.")
            self.question_display.setStyleSheet("color: black; background: rgba(236,239,241,0.7); border-radius: 10px;")
            self.stop_submit = True
            self.answer_selection = None
            return

        self.stop_submit = False

        n = random.randint(0, len(self.questions) - 1)
        self.question_comp = self.questions[n]
        self.question_id = self.question_comp[0]
        self.question = self.question_comp[1]
        self.answer = self.question_comp[2]

        self.question_display.setText(self.question)

        self.questions.remove(self.question_comp)

        # self.submit_btn.clicked.connect(self.none)

        self.option_group.setExclusive(False)
        self.option_a.setChecked(False)
        # self.option_a_label.setStyleSheet("background-color: rgba(0,0,0,0)")
        # self.option_a.setChecked(True)
        self.option_b.setChecked(False)
        # self.option_b_label.setStyleSheet("background-color: rgba(0,0,0,0)")
        # self.option_b.setChecked(True)
        self.option_c.setChecked(False)
        # self.option_c_label.setStyleSheet("background-color: rgba(0,0,0,0)")
        # self.option_c.setChecked(True)
        self.option_d.setChecked(False)
        # self.option_d_label.setStyleSheet("background-color: rgba(0,0,0,0)")
        # self.option_d.setChecked(True)
        self.option_group.setExclusive(True)

        relations = [
            self.option_a_label,
            self.option_b_label,
            self.option_c_label,
            self.option_d_label
        ]

        for x in relations:
            x.setStyleSheet("")

        self.submit_btn.show()

        arrangement = [(2, 3, 4, 5), (4, 3, 2, 5), (3, 5, 4, 2), (3, 2, 5, 4)]
        arr = arrangement[random.randint(0, 3)]
        op1 = arr[0]
        op2 = arr[1]
        op3 = arr[2]
        op4 = arr[3]

        self.option1 = self.question_comp[op1]
        self.option2 = self.question_comp[op2]
        self.option3 = self.question_comp[op3]
        self.option4 = self.question_comp[op4]

        self.option_a_label.setText(self.option1)
        self.option_b_label.setText(self.option2)
        self.option_c_label.setText(self.option3)
        self.option_d_label.setText(self.option4)

        self.option_a_label.clicked.connect(lambda: self.answer_select(self.option_a_label))
        self.option_a.toggled.connect(lambda: self.option_a_label.clicked.emit())
        self.option_b_label.clicked.connect(lambda: self.answer_select(self.option_b_label))
        self.option_b.toggled.connect(lambda: self.option_b_label.clicked.emit())
        self.option_c_label.clicked.connect(lambda: self.answer_select(self.option_c_label))
        self.option_c.toggled.connect(lambda: self.option_c_label.clicked.emit())
        self.option_d_label.clicked.connect(lambda: self.answer_select(self.option_d_label))
        self.option_d.toggled.connect(lambda: self.option_d_label.clicked.emit())

        # self.option_a.toggled.connect(lambda: self.answer_select(self.option_a_label))
        # self.option_b.toggled.connect(lambda: self.answer_select(self.option_b_label))
        # self.option_c.toggled.connect(lambda: self.answer_select(self.option_c_label))
        # self.option_d.toggled.connect(lambda: self.answer_select(self.option_d_label))

        # self.option_a.setChecked(True)

        self.submit_btn.setEnabled(False)

        self.answer_selection = None
        app.aboutToQuit.connect(self.client.disconnect)

    def answer_select(self, selection):  # Quiz Sub-function
        if self.stop_submit == True:
            return
        self.answer_selection = selection.text()
        # self.option_a_label.setStyleSheet("background-color: rgba(255,255,255,0)")
        # self.option_b_label.setStyleSheet("background-color: rgba(255,255,255,0)")
        # self.option_c_label.setStyleSheet("background-color: rgba(255,255,255,0)")
        # self.option_d_label.setStyleSheet("background-color: rgba(255,255,255,0)")

        relations = [
            self.option_a_label,
            self.option_b_label,
            self.option_c_label,
            self.option_d_label
        ]

        for x in relations:
            x.setStyleSheet("")

        selection.setStyleSheet("border: lightblue; border-width: 5px; border-style: solid; background: rgba(236,239,241,0.8);")

        '''
        if self.answer_selection == self.answer:
            choice.setStyleSheet("background-color: rgba(24,255,0,0.75)")
        else:
            choice.setStyleSheet("background-color: rgba(255,0,0,0.75)")'''
        # self.option_a.setStyleSheet("color: #10FF00; background-color: white")

        self.submit_btn.setEnabled(True)
        app.aboutToQuit.connect(self.client.disconnect)

    def submit_final_answer(self):  # Quiz Sub-function
        if self.answer_selection == None:
            return

        self.finalize_btn.setEnabled(True)
        question = answer()
        question.setup(self.question_id, self.question, self.answer, self.option1, self.option2, self.option3,
                       self.option4, self.answer_selection)
        self.history.append(question)
        self.question_count.display(len(self.history))
        # print(question)
        # print(self.history)
        x = self.history[-1]
        '''
        if x.answer_select == x.correct_answer:
            print("true")
        else:
            print("false")
        '''
        self.score_inserted = False
        self.quiz()

    def answer_confirm(self, MainWindow):  # Quiz Sub-function
        self.answer_confirm_screen = QtWidgets.QWidget(MainWindow)
        self.answer_confirm_screen.setObjectName("answer_confirm_screen")

        self.home_btn = QtWidgets.QPushButton(self.answer_confirm_screen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.answer_confirm_screen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))

        self.answers_table = QtWidgets.QTableWidget(self.answer_confirm_screen)
        self.answers_table.setGeometry(QtCore.QRect(40, 240, 1275, 375))
        # self.answers_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.answers_table.setTabKeyNavigation(True)
        self.answers_table.setObjectName("answers_table")
        self.answers_table.setColumnCount(2)
        self.answers_table.setSortingEnabled(True)
        self.answers_table.setRowCount(len(self.history))
        self.answers_table.horizontalHeader().setMinimumSectionSize(600)
        self.answers_table.verticalHeader().setDefaultSectionSize(60)
        self.answers_table.setAlternatingRowColors(True)
        item = QtWidgets.QTableWidgetItem()
        self.answers_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.answers_table.setHorizontalHeaderItem(1, item)
        self.logo = QtWidgets.QLabel(self.answer_confirm_screen)
        self.logo.setGeometry(QtCore.QRect(605, 20, 150, 150))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap(LOGO))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.label_answer_confirm = QtWidgets.QLabel(self.answer_confirm_screen)
        self.label_answer_confirm.setGeometry(QtCore.QRect(40, 180, 1000, 50))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.label_answer_confirm.setFont(font)
        self.label_answer_confirm.setObjectName("label_answer_confirm")
        self.check_answers_btn = QtWidgets.QPushButton(self.answer_confirm_screen)
        self.check_answers_btn.setGeometry(QtCore.QRect(587, 635, 180, 50))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.check_answers_btn.setFont(font)
        self.check_answers_btn.setObjectName("check_answers_btn")
        MainWindow.setCentralWidget(self.answer_confirm_screen)

        item = self.answers_table.horizontalHeaderItem(0)
        item.setText("Question")
        item = self.answers_table.horizontalHeaderItem(1)
        item.setText("Answer Choice")
        self.label_answer_confirm.setText(
            "Please recheck and confirm your answers. Double-click the answer you wish to correct.")
        self.check_answers_btn.setText("Calculate Score")

        for x in self.history:
            number = self.history.index(x)
            item = QtWidgets.QTableWidgetItem()

            item.setText(f"Question no. {number + 1}")
            item = self.answers_table.verticalHeaderItem(number)

            question = qtw.QTableWidgetItem()
            self.answers_table.setItem(number, 0, question)
            question.setText(x.question)
            question.setFlags(QtCore.Qt.ItemIsEnabled)
            # question.itemDoubleClicked.connect(lambda: self.answer_correction(x, MainWindow))

            answer_select = qtw.QTableWidgetItem()
            self.answers_table.setItem(number, 1, answer_select)
            answer_select.setText(x.answer_select)
            answer_select.setFlags(QtCore.Qt.ItemIsEnabled)
            # answer_select.itemDoubleClicked.connect(lambda: self.answer_correction(x, MainWindow))
            # answer_select.setStyleSheet("background-color: rgba(24,255,0,0.65)")
            if self.check_clicked == True:
                if x.answer_select == x.correct_answer:
                    self.answers_table.item(number, 1).setBackground(QtGui.QColor(60, 255, 0))
                else:
                    self.answers_table.item(number, 1).setBackground(QtGui.QColor(255, 30, 0))

        self.answers_table.isEditable = False
        self.answers_table.itemDoubleClicked.connect(lambda x: self.answer_correction(x.row(), MainWindow))
        self.answers_table.itemClicked.connect(lambda x: self.answer_correction(x.row(), MainWindow))
        self.answers_table.itemDoubleClicked.connect(lambda x: self.review_answer(x.row(), MainWindow))
        self.answers_table.itemClicked.connect(lambda x: self.review_answer(x.row(), MainWindow))
        self.check_answers_btn.clicked.connect(lambda: self.check(MainWindow))
        self.check_answers_btn.setEnabled(True)

        app.aboutToQuit.connect(self.client.disconnect)

    def check(self, MainWindow):
        if self.check_clicked == True:
            return
        self.check_clicked = True
        self.answer_confirm(MainWindow)
        self.check_answers_btn.setEnabled(False)

        correct = 0
        total = len(self.history)
        for x in self.history:
            if x.correct_answer == x.answer_select:
                correct += 1
        self.label_answer_confirm.setText(
            f"These are your results. You scored {correct} out of {total}. Double-click on any question to see its "
            f"correct answer. ")
        if self.score_inserted == False:
            std_id, subject_select = self.student_id, self.subject_select
            self.client.query_sql(
                "INSERT INTO score (student, subject, correct_answers, total_answers) VALUES (%s, %s, %s, %s)",
                (std_id, subject_select, correct, total))
        self.score_inserted = True

        app.aboutToQuit.connect(self.client.disconnect)

    def answer_correction(self, question_index, MainWindow):
        if self.check_clicked == True:
            return

        self.answer_confirm_screen.hide()

        self.check_answer_window = qtw.QWidget(MainWindow)
        self.check_answer_window.setObjectName("check_answer_window")

        self.home_btn = QtWidgets.QPushButton(self.check_answer_window)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.check_answer_window)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))

        self.gridWidget = QtWidgets.QWidget(self.check_answer_window)
        self.gridWidget.setGeometry(QtCore.QRect(0, 300, 1355, 281))
        self.gridWidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Pakistan))
        self.gridWidget.setObjectName("gridWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setContentsMargins(40, 30, 0, 0)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.option_b = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_b.setFont(font)
        self.option_b.setObjectName("option_b")
        self.gridLayout.addWidget(self.option_b, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_c_label = ClickableLabel(self.gridWidget)
        self.option_c_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_c_label.setFont(font)
        self.option_c_label.setWordWrap(True)
        self.option_c_label.setObjectName("option_c_label")
        self.gridLayout.addWidget(self.option_c_label, 0, 3, 1, 1, QtCore.Qt.AlignLeft)
        self.option_a_label = ClickableLabel(self.gridWidget)
        self.option_a_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_a_label.setFont(font)
        self.option_a_label.setAutoFillBackground(False)
        self.option_a_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.option_a_label.setWordWrap(True)
        self.option_a_label.setObjectName("option_a_label")
        self.gridLayout.addWidget(self.option_a_label, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.option_d = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_d.setFont(font)
        self.option_d.setObjectName("option_d")
        self.gridLayout.addWidget(self.option_d, 2, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_b_label = ClickableLabel(self.gridWidget)
        self.option_b_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_b_label.setFont(font)
        self.option_b_label.setWordWrap(True)
        self.option_b_label.setObjectName("option_b_label")
        self.gridLayout.addWidget(self.option_b_label, 2, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.option_c = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_c.setFont(font)
        self.option_c.setObjectName("option_c")
        self.gridLayout.addWidget(self.option_c, 0, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_a = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_a.setFont(font)
        self.option_a.setObjectName("option_a")
        self.gridLayout.addWidget(self.option_a, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_d_label = ClickableLabel(self.gridWidget)
        self.option_d_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_d_label.setFont(font)
        self.option_d_label.setWordWrap(True)
        self.option_d_label.setObjectName("option_d_label")
        self.gridLayout.addWidget(self.option_d_label, 2, 3, 1, 1, QtCore.Qt.AlignLeft)
        self.gridLayout.setColumnMinimumWidth(0, 40)
        self.gridLayout.setColumnMinimumWidth(1, 650)
        self.gridLayout.setColumnMinimumWidth(2, 40)
        self.gridLayout.setColumnMinimumWidth(3, 650)
        self.gridLayout.setRowMinimumHeight(0, 75)
        self.gridLayout.setRowMinimumHeight(1, 75)
        self.gridLayout.setColumnStretch(0, 20)
        self.gridLayout.setColumnStretch(1, 500)
        self.gridLayout.setColumnStretch(2, 20)
        self.gridLayout.setColumnStretch(3, 500)
        self.gridLayout.setRowStretch(0, 75)
        self.gridLayout.setRowStretch(2, 75)
        self.logo = QtWidgets.QLabel(self.check_answer_window)
        self.logo.setGeometry(QtCore.QRect(595, 10, 180, 180))
        self.logo.setMinimumSize(QtCore.QSize(150, 150))
        self.logo.setMaximumSize(QtCore.QSize(200, 200))
        self.logo.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Pakistan))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap(LOGO))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")

        self.confirm_answer_btn = QtWidgets.QPushButton(self.check_answer_window)
        self.confirm_answer_btn.setGeometry(QtCore.QRect(370, 600, 600, 60))
        self.confirm_answer_btn.setMinimumSize(QtCore.QSize(600, 60))
        self.confirm_answer_btn.setMaximumSize(QtCore.QSize(600, 16777215))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(22)
        self.confirm_answer_btn.setFont(font)
        self.confirm_answer_btn.setObjectName("confirm_answer_btn")

        self.question_display = QtWidgets.QTextBrowser(self.check_answer_window)
        self.question_display.setGeometry(QtCore.QRect(126, 210, 1100, 100))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.question_display.setFont(font)
        self.question_display.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.question_display.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.question_display.setObjectName("question_display")
        # self.question_display.setStyleSheet("background-color: rgba(255,255,255,0)")

        self.option_group = QtWidgets.QButtonGroup(self.check_answer_window)
        self.option_group.addButton(self.option_a)
        self.option_group.addButton(self.option_b)
        self.option_group.addButton(self.option_c)
        self.option_group.addButton(self.option_d)

        question = self.history[question_index]
        self.question_display.setText(question.question)
        self.option_a_label.setText(question.option_a)
        self.option_b_label.setText(question.option_b)
        self.option_c_label.setText(question.option_c)
        self.option_d_label.setText(question.option_d)

        choices = [(question.option_a, self.option_a, self.option_a_label),
                   (question.option_b, self.option_b, self.option_b_label),
                   (question.option_c, self.option_c, self.option_c_label),
                   (question.option_d, self.option_d, self.option_d_label)]
        for x in choices:
            if question.answer_select == x[0]:
                # x[1].setChecked(True)
                self.answer_correct(x[2], question)

        self.option_a.toggled.connect(lambda: self.answer_correct(self.option_a_label, question))
        self.option_a_label.clicked.connect(lambda: self.answer_correct(self.option_a_label, question))
        self.option_b.toggled.connect(lambda: self.answer_correct(self.option_b_label, question))
        self.option_b_label.clicked.connect(lambda: self.answer_correct(self.option_b_label, question))
        self.option_c.toggled.connect(lambda: self.answer_correct(self.option_c_label, question))
        self.option_c_label.clicked.connect(lambda: self.answer_correct(self.option_c_label, question))
        self.option_d.toggled.connect(lambda: self.answer_correct(self.option_d_label, question))
        self.option_d_label.clicked.connect(lambda: self.answer_correct(self.option_d_label, question))

        # self.answer_selection = None

        self.confirm_answer_btn.clicked.connect(lambda: self.confirm_answer(question, MainWindow))

        self.option_a.setText("A:")
        self.option_b.setText("B:")
        self.option_c.setText("C:")
        self.option_d.setText("D:")
        self.confirm_answer_btn.setText("Confirm Answer")



        # self.confirm_answer_btn.setEnabled(False)

        MainWindow.setCentralWidget(self.check_answer_window)
        app.aboutToQuit.connect(self.client.disconnect)

    def answer_correct(self, selection, question):  # Quiz Sub-function
        self.answer_selection = selection.text()
        # self.option_a_label.setStyleSheet("background-color: rgba(255,255,255,0)")
        # self.option_b_label.setStyleSheet("background-color: rgba(255,255,255,0)")
        # self.option_c_label.setStyleSheet("background-color: rgba(255,255,255,0)")
        # self.option_d_label.setStyleSheet("background-color: rgba(255,255,255,0)")
        choice = selection
        '''
        if self.answer_selection == question.correct_answer:
            choice.setStyleSheet("background-color: rgba(24,255,0,0.65)")
        else:
            choice.setStyleSheet("background-color: rgba(255,0,0,0.65)")
            '''

        relations = [
            self.option_a_label,
            self.option_b_label,
            self.option_c_label,
            self.option_d_label
        ]

        for x in relations:
            x.setStyleSheet("")

        selection.setStyleSheet(
            "border: lightblue; border-width: 5px; border-style: solid; background: rgba(236,239,241,0.8);")

        self.confirm_answer_btn.setEnabled(True)
        app.aboutToQuit.connect(self.client.disconnect)

    def confirm_answer(self, question, MainWindow):
        if self.answer_selection == None:
            return
        question.correct(self.answer_selection)
        self.check_answer_window.hide()
        self.answer_confirm(MainWindow)

        app.aboutToQuit.connect(self.client.disconnect)

    def review_answer(self, question_index, MainWindow):
        if self.check_clicked is False:
            return

        self.answer_confirm_screen.hide()

        self.review_answer_window = qtw.QWidget(MainWindow)
        self.review_answer_window.setObjectName("review_answer_window")

        self.home_btn = QtWidgets.QPushButton(self.review_answer_window)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.review_answer_window)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))

        self.gridWidget = QtWidgets.QWidget(self.review_answer_window)
        self.gridWidget.setGeometry(QtCore.QRect(0, 300, 1355, 281))
        self.gridWidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Pakistan))
        self.gridWidget.setObjectName("gridWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridWidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setContentsMargins(40, 30, 0, 0)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.option_b = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_b.setFont(font)
        self.option_b.setObjectName("option_b")
        self.gridLayout.addWidget(self.option_b, 2, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_c_label = QtWidgets.QLabel(self.gridWidget)
        self.option_c_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_c_label.setFont(font)
        self.option_c_label.setWordWrap(True)
        self.option_c_label.setObjectName("option_c_label")
        self.gridLayout.addWidget(self.option_c_label, 0, 3, 1, 1, QtCore.Qt.AlignLeft)
        self.option_a_label = QtWidgets.QLabel(self.gridWidget)
        self.option_a_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_a_label.setFont(font)
        self.option_a_label.setAutoFillBackground(False)
        self.option_a_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.option_a_label.setWordWrap(True)
        self.option_a_label.setObjectName("option_a_label")
        self.gridLayout.addWidget(self.option_a_label, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.option_d = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_d.setFont(font)
        self.option_d.setObjectName("option_d")
        self.gridLayout.addWidget(self.option_d, 2, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_b_label = QtWidgets.QLabel(self.gridWidget)
        self.option_b_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_b_label.setFont(font)
        self.option_b_label.setWordWrap(True)
        self.option_b_label.setObjectName("option_b_label")
        self.gridLayout.addWidget(self.option_b_label, 2, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.option_c = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_c.setFont(font)
        self.option_c.setObjectName("option_c")
        self.gridLayout.addWidget(self.option_c, 0, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_a = QtWidgets.QRadioButton(self.gridWidget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_a.setFont(font)
        self.option_a.setObjectName("option_a")
        self.gridLayout.addWidget(self.option_a, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.option_d_label = QtWidgets.QLabel(self.gridWidget)
        self.option_d_label.setMinimumSize(QtCore.QSize(550, 75))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.option_d_label.setFont(font)
        self.option_d_label.setWordWrap(True)
        self.option_d_label.setObjectName("option_d_label")
        self.gridLayout.addWidget(self.option_d_label, 2, 3, 1, 1, QtCore.Qt.AlignLeft)
        self.gridLayout.setColumnMinimumWidth(0, 40)
        self.gridLayout.setColumnMinimumWidth(1, 650)
        self.gridLayout.setColumnMinimumWidth(2, 40)
        self.gridLayout.setColumnMinimumWidth(3, 650)
        self.gridLayout.setRowMinimumHeight(0, 75)
        self.gridLayout.setRowMinimumHeight(1, 75)
        self.gridLayout.setColumnStretch(0, 20)
        self.gridLayout.setColumnStretch(1, 500)
        self.gridLayout.setColumnStretch(2, 20)
        self.gridLayout.setColumnStretch(3, 500)
        self.gridLayout.setRowStretch(0, 75)
        self.gridLayout.setRowStretch(2, 75)
        self.logo = QtWidgets.QLabel(self.review_answer_window)
        self.logo.setGeometry(QtCore.QRect(595, 10, 180, 180))
        self.logo.setMinimumSize(QtCore.QSize(150, 150))
        self.logo.setMaximumSize(QtCore.QSize(200, 200))
        self.logo.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Pakistan))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap(LOGO))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")

        self.question_display = QtWidgets.QTextBrowser(self.review_answer_window)
        self.question_display.setGeometry(QtCore.QRect(126, 210, 1100, 100))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.question_display.setFont(font)
        self.question_display.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.question_display.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.question_display.setObjectName("question_display")
        # self.question_display.setStyleSheet("background-color: rgba(255,255,255,0)")

        self.option_group = QtWidgets.QButtonGroup(self.review_answer_window)
        self.option_group.addButton(self.option_a)
        self.option_group.addButton(self.option_b)
        self.option_group.addButton(self.option_c)
        self.option_group.addButton(self.option_d)

        question = self.history[question_index]
        self.question_display.setText(question.question)
        self.option_a_label.setText(question.option_a)
        self.option_b_label.setText(question.option_b)
        self.option_c_label.setText(question.option_c)
        self.option_d_label.setText(question.option_d)

        choices = [(question.option_a, self.option_a, self.option_a_label),
                   (question.option_b, self.option_b, self.option_b_label),
                   (question.option_c, self.option_c, self.option_c_label),
                   (question.option_d, self.option_d, self.option_d_label)]

        for x in choices:
            if x[0] == question.correct_answer:
                x[2].setStyleSheet("background-color: rgba(24,255,0,0.75); border-radius: 10px; border-left-width: "
                                   "2px; border-style: solid; border-color: rgba(24,255,0,0.75)")
            elif x[0] == question.answer_select and x[0] != question.correct_answer:
                x[1].setChecked(True)
                x[2].setStyleSheet("background-color: rgba(255,0,0,0.75); border-radius: 10px; border-left-width: "
                                   "2px; border-style: solid; border-color: rgba(255,0,0,0.75)")
            else:
                # x[2].setStyleSheet("background-color: rgba(255,255,255,0)")
                pass
            x[1].setEnabled(False)

        self.back_answers_btn = qtw.QPushButton(self.review_answer_window)
        self.back_answers_btn.setObjectName("back_answers_btn")
        self.back_answers_btn.setGeometry(QtCore.QRect(370, 600, 600, 60))
        self.back_answers_btn.setText("Return")
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(22)
        self.back_answers_btn.setFont(font)
        self.back_answers_btn.clicked.connect(lambda: self.back_answer(MainWindow))

        self.option_a.setText("A:")
        self.option_b.setText("B:")
        self.option_c.setText("C:")
        self.option_d.setText("D:")

        MainWindow.setCentralWidget(self.review_answer_window)
        app.aboutToQuit.connect(self.client.disconnect)

    def back_answer(self, MainWindow):
        self.review_answer_window.hide()
        self.check_clicked = False
        self.check(MainWindow)

    def studentUpdateProfile(self, MainWindow):
        self.studentUpdateScreen = QtWidgets.QWidget(MainWindow)
        self.studentUpdateScreen.setObjectName("studentUpdateScreen")

        self.home_btn = QtWidgets.QPushButton(self.studentUpdateScreen)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.studentUpdateScreen)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))

        self.verticalWidget = QtWidgets.QWidget(self.studentUpdateScreen)
        self.verticalWidget.setGeometry(QtCore.QRect(0, 0, 1355, 700))
        self.verticalWidget.setObjectName("verticalWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalWidget)
        self.verticalLayout.setContentsMargins(20, 10, 20, 20)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_6 = QtWidgets.QLabel(self.verticalWidget)
        self.label_6.setMaximumSize(QtCore.QSize(150, 150))
        self.label_6.setLineWidth(0)
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap(LOGO))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6, 0, QtCore.Qt.AlignHCenter)

        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)

        self.details_label = QtWidgets.QLabel(self.verticalWidget)
        self.details_label.setMinimumSize(QtCore.QSize(0, 0))
        self.details_label.setMaximumSize(QtCore.QSize(200, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(24)
        self.details_label.setFont(font)
        self.details_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.details_label.setObjectName("details_label")
        self.verticalLayout.addWidget(self.details_label)

        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)

        self.name_label = QtWidgets.QLabel(self.verticalWidget)
        self.name_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.name_label.setFont(font)
        self.name_label.setObjectName("name_label")
        self.verticalLayout.addWidget(self.name_label)

        self.nameEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.nameEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.nameEdit.setFont(font)
        self.nameEdit.setObjectName("nameEdit")
        self.verticalLayout.addWidget(self.nameEdit)

        spacerItem2 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)

        self.email_label = QtWidgets.QLabel(self.verticalWidget)
        self.email_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.email_label.setFont(font)
        self.email_label.setObjectName("email_label")
        self.verticalLayout.addWidget(self.email_label)

        self.emailEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.emailEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.emailEdit.setFont(font)
        self.emailEdit.setObjectName("emailEdit")
        self.verticalLayout.addWidget(self.emailEdit)

        spacerItem3 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem3)

        self.password_label = QtWidgets.QLabel(self.verticalWidget)
        self.password_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.verticalLayout.addWidget(self.password_label)

        self.passwordEdit = QtWidgets.QLineEdit(self.verticalWidget)
        self.passwordEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.passwordEdit.setFont(font)
        self.passwordEdit.setObjectName("passwordEdit")
        self.verticalLayout.addWidget(self.passwordEdit)

        spacerItem4 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem4)

        self.class_label = QtWidgets.QLabel(self.verticalWidget)
        self.class_label.setMaximumSize(QtCore.QSize(200, 40))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.class_label.setFont(font)
        self.class_label.setObjectName("class_label")
        self.verticalLayout.addWidget(self.class_label)

        self.classEdit = QtWidgets.QComboBox(self.verticalWidget)
        self.classEdit.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(15)
        self.classEdit.setFont(font)
        self.classEdit.setObjectName("classEdit")
        self.verticalLayout.addWidget(self.classEdit)

        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem5)

        self.applyChanges_btn = QtWidgets.QPushButton(self.verticalWidget)
        self.applyChanges_btn.setMinimumSize(QtCore.QSize(0, 50))
        self.applyChanges_btn.setObjectName("applyChanges_btn")
        self.applyChanges_btn.setFont(font)
        self.applyChanges_btn.clicked.connect(lambda: self.apply_student_changes(self.student_id))
        self.verticalLayout.addWidget(self.applyChanges_btn)

        MainWindow.setCentralWidget(self.studentUpdateScreen)

        self.details_label.setText("Your Details:")
        self.name_label.setText("Name")
        self.email_label.setText("E-mail")
        self.password_label.setText("Password")
        self.class_label.setText("Class")
        self.applyChanges_btn.setText("Apply changes")

        grades = [
            ("Junior 1 - A", "Jr1A"),
            ("Junior 1 - B", "Jr1B"),
            ("Junior 2 - A", "Jr2A"),
            ("Junior 2 - B", "Jr2B"),
            ("Senior 1 - A", "Sr1A"),
            ("Senior 1 - B", "Sr1B"),
            ("Senior 2 - A", "Sr2A"),
            ("Senior 2 - B", "Sr2B"),
            ("Senior 3 - A", "Sr3A"),
            ("Senior 3 - B", "Sr3B")
        ]

        std_id = self.student_id
        select = self.client.query_sql("SELECT * FROM students WHERE student_id = %s", (std_id,))
        for x in select:
            self.name = x[1]
            self.email = x[2]
            self.password = x[3]
            self.grade = x[4]

        self.nameEdit.setText(self.name)
        self.emailEdit.setText(self.email)
        self.passwordEdit.setText(self.password)
        # self.classEdit.addItem(self.grade)

        # grades.remove(self.grade)
        for x in grades:
            self.classEdit.addItem(*x)
            if self.grade == x[1]:
                self.grade = x[0]

        self.classEdit.setCurrentText(self.grade)

        self.home_btn.raise_()
        self.logout_btn.raise_()

        app.aboutToQuit.connect(self.client.disconnect)

    def apply_student_changes(self, std_id):
        name = self.nameEdit.text()
        email = self.emailEdit.text()
        password = self.passwordEdit.text()
        class_ = self.classEdit.currentData()

        self.client.query_sql("UPDATE students SET name = %s, email = %s, password = %s, class = %s WHERE student_id "
                              "= %s", (name, email, password, class_, std_id))

        select = self.client.query_sql("SELECT * FROM students WHERE student_id = %s", (std_id,))
        for x in select:
            self.name = x[1]
            self.email = x[2]
            self.grade = x[4]
            # print(self.name, self.email, self.grade)
        app.aboutToQuit.connect(self.client.disconnect)

    def studentViewScore(self, MainWindow):
        self.student_score_view = QtWidgets.QWidget(MainWindow)
        self.student_score_view.setObjectName("student_score_view")

        self.home_btn = QtWidgets.QPushButton(self.student_score_view)
        self.home_btn.setObjectName("home_btn")
        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.home_btn.setGeometry(QtCore.QRect(1280, 20, 55, 55))
        # self.home_btn.setText("Home")
        home_icon = QtGui.QIcon()
        home_icon.addPixmap(QtGui.QPixmap("Images/home_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.home_btn.setIcon(home_icon)
        self.home_btn.setIconSize(qtc.QSize(50, 50))
        self.home_btn.show()

        self.logout_btn = QtWidgets.QPushButton(self.student_score_view)
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))
        self.logout_btn.setGeometry(QtCore.QRect(1280, 80, 55, 55))
        logout_icon = QtGui.QIcon()
        logout_icon.addPixmap(QtGui.QPixmap("Images/logout_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.logout_btn.setIcon(logout_icon)
        self.logout_btn.setIconSize(QtCore.QSize(50, 50))
        self.logout_btn.show()

        self.home_btn.clicked.connect(lambda: self.student_home(MainWindow))
        self.logout_btn.clicked.connect(lambda: self.logout(MainWindow))

        self.create_rep_btn = qtw.QPushButton(self.student_score_view)
        self.create_rep_btn.setGeometry(QtCore.QRect(430, 640, 500, 50))
        self.create_rep_btn.setObjectName("create_rep_btn")
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.create_rep_btn.setFont(font)
        self.create_rep_btn.setText("Create PDF Report")

        self.score_display = QtWidgets.QTableWidget(self.student_score_view)
        self.score_display.setEnabled(True)
        self.score_display.setSortingEnabled(True)
        self.score_display.setStyleSheet("color: black; background: rgba(236,239,241,0.7); border-radius: 10px;")
        self.score_display.setGeometry(QtCore.QRect(30, 245, 1301, 380))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(18)
        self.score_display.setFont(font)
        self.score_display.setAlternatingRowColors(True)
        self.score_display.setGridStyle(QtCore.Qt.SolidLine)
        self.score_display.setCornerButtonEnabled(True)
        self.score_display.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.score_display.setObjectName("score_display")
        self.score_display.setColumnCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(0, item)
        self.score_display.setColumnWidth(0, 300)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(1, item)
        self.score_display.setColumnWidth(1, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(2, item)
        self.score_display.setColumnWidth(2, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(3, item)
        self.score_display.setColumnWidth(3, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(4, item)
        self.score_display.horizontalHeader().setStretchLastSection(True)
        # self.score_display.horizontalHeader().setDefaultSectionSize(256)
        self.logo_label = QtWidgets.QLabel(self.student_score_view)
        self.logo_label.setGeometry(QtCore.QRect(608, 10, 150, 150))
        self.logo_label.setText("")
        self.logo_label.setPixmap(QtGui.QPixmap(LOGO))
        self.logo_label.setScaledContents(True)
        self.logo_label.setObjectName("logo_label")
        self.label = QtWidgets.QLabel(self.student_score_view)
        self.label.setGeometry(QtCore.QRect(35, 175, 1280, 60))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.back_btn = QPushButton(self.student_score_view)
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setGeometry(QtCore.QRect(15, 15, 55, 55))
        # self.back_btn.setText("Go Back")
        self.back_btn.clicked.connect(lambda: self.studentViewScore(MainWindow))
        back_icon = QtGui.QIcon()
        back_icon.addPixmap(QtGui.QPixmap("Images/return.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.back_btn.setIcon(back_icon)
        self.back_btn.setIconSize(QtCore.QSize(45, 45))
        self.back_btn.hide()
        MainWindow.setCentralWidget(self.student_score_view)

        item = self.score_display.horizontalHeaderItem(0)
        item.setText("Subject")
        item = self.score_display.horizontalHeaderItem(1)
        item.setText("Correct Answers")
        item = self.score_display.horizontalHeaderItem(2)
        item.setText("Total Answers")
        item = self.score_display.horizontalHeaderItem(3)
        item.setText("Percentage")
        item = self.score_display.horizontalHeaderItem(4)
        item.setText("Last Updated")
        self.label.setText("Double-click a subject for its complete score history.")

        self.subjects = []
        select = self.client.query_sql(
            "SELECT student, subject, date_of_entry, correct_answers, total_answers FROM score WHERE "
            "student = %s", (self.student_id,))
        for x in select:
            # print(x)
            if len(self.subjects) == 0:
                score = subject_score()
                score.setup(x[1])
                score.add_score(x[3], x[4], x[2])
                self.subjects.append(score)
                # print(subjects)

            else:
                inlist = False
                for y in self.subjects:
                    if x[1] == y.name:
                        inlist = True
                        subject = y
                        break

                if inlist == True:
                    subject.add_score(x[3], x[4], x[2])
                    # print(subjects)

                else:
                    score = subject_score()
                    score.setup(x[1])
                    self.subjects.append(score)
                    score.add_score(x[3], x[4], x[2])
                    # print(subjects)

        self.create_rep_btn.clicked.connect(lambda: self.create_report(self.student_id, self.subjects))

        self.score_display.setRowCount(len(self.subjects))
        # print(len(subjects))

        if len(self.subjects) == 0:
            self.label.setText("You don't have any score records. Take a quiz and then come back.")

        for number, object in enumerate(self.subjects):
            # number = x[0]
            # object = x[1]
            correct = 0
            total = 0

            entry = qtw.QTableWidgetItem()
            self.score_display.setVerticalHeaderItem(number, entry)
            entry.setText(str(number + 1))

            subject = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 0, subject)
            subject.setText(object.display_name)
            subject.setFlags(qtc.Qt.ItemIsEnabled)
            subject.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            scored = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 1, scored)
            for y in object.scores:
                correct += y[0]
                total += y[1]
            scored.setText(str(correct))
            scored.setFlags(qtc.Qt.ItemIsEnabled)
            scored.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            total_answered = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 2, total_answered)
            total_answered.setText(str(total))
            total_answered.setFlags(qtc.Qt.ItemIsEnabled)
            total_answered.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            percentage = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 3, percentage)
            percentage.setText(f"{object.percentage()}%")
            percentage.setFlags(qtc.Qt.ItemIsEnabled)
            percentage.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            date = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 4, date)
            date.setText(f"{object.last_date}")
            date.setFlags(qtc.Qt.ItemIsEnabled)
            date.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

        self.score_display.isEditable = False
        self.score_history_disable = False
        self.score_display.itemDoubleClicked.connect(lambda x: self.score_history(x))
        self.score_display.itemClicked.connect(lambda x: self.score_history(x))

        app.aboutToQuit.connect(self.client.disconnect)

    def score_history(self, row):
        if self.score_history_disable is True:
            return

        subject_item = self.subjects[row.row()]
        self.score_display.clear()
        self.score_display.setRowCount(len(subject_item.scores))

        self.label.setText(f"Score History for {subject_item.display_name}")

        # self.score_display.setColumnCount(0)
        # self.score_display.setColumnCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(0, item)
        self.score_display.setColumnWidth(0, 300)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(1, item)
        self.score_display.setColumnWidth(1, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(2, item)
        self.score_display.setColumnWidth(2, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(3, item)
        self.score_display.setColumnWidth(3, 200)
        item = QtWidgets.QTableWidgetItem()
        self.score_display.setHorizontalHeaderItem(4, item)
        self.score_display.horizontalHeader().setStretchLastSection(True)

        item = self.score_display.horizontalHeaderItem(0)
        item.setText("Subject")
        item = self.score_display.horizontalHeaderItem(1)
        item.setText("Correct Answers")
        item = self.score_display.horizontalHeaderItem(2)
        item.setText("Total Answers")
        item = self.score_display.horizontalHeaderItem(3)
        item.setText("Percentage")
        item = self.score_display.horizontalHeaderItem(4)
        item.setText("Last Updated")

        for number, compound in enumerate(subject_item.scores):
            entry = qtw.QTableWidgetItem()
            self.score_display.setVerticalHeaderItem(number, entry)
            entry.setText(str(number + 1))

            subject = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 0, subject)
            subject.setText(subject_item.display_name)
            subject.setFlags(qtc.Qt.ItemIsEnabled)
            subject.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            scored = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 1, scored)
            scored.setText(str(compound[0]))
            scored.setFlags(Qt.ItemIsEnabled)
            scored.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            total_score = QTableWidgetItem()
            self.score_display.setItem(number, 2, total_score)
            total_score.setText(str(compound[1]))
            total_score.setFlags(Qt.ItemIsEnabled)
            total_score.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

            percentage = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 3, percentage)
            percentage.setText(f"{(round((compound[0] / compound[1] * 100), 2))}%")
            percentage.setFlags(qtc.Qt.ItemIsEnabled)
            percentage.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

            date = qtw.QTableWidgetItem()
            self.score_display.setItem(number, 4, date)
            date.setText(str((compound[2]).strftime("%H:%M %a, %d %B %Y")))
            date.setFlags(qtc.Qt.ItemIsEnabled)
            date.setTextAlignment(qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter)

        self.back_btn.show()
        self.score_history_disable = True
        app.aboutToQuit.connect(self.client.disconnect)

    def create_report(self, std_id, data):
        select = self.client.query_sql("SELECT name, class FROM students WHERE student_id = %s", (std_id, ))
        for x in select:
            student_name = x[0]
            student_class = x[1]

        grades = [
            ("Junior 1 - A", "Jr1A"),
            ("Junior 1 - B", "Jr1B"),
            ("Junior 2 - A", "Jr2A"),
            ("Junior 2 - B", "Jr2B"),
            ("Senior 1 - A", "Sr1A"),
            ("Senior 1 - B", "Sr1B"),
            ("Senior 2 - A", "Sr2A"),
            ("Senior 2 - B", "Sr2B"),
            ("Senior 3 - A", "Sr3A"),
            ("Senior 3 - B", "Sr3B")
        ]

        for x in grades:
            if student_class == x[1]:
                student_class= x[0]

        contents = [["Subject", "Correct Answers", "Total Answers", "Percentage", "Last Updated"]]
        percentages = []

        for x in data:
            c_ans = 0
            ans = 0

            subject = x.display_name

            for y in x.scores:
                c_ans += y[0]
                ans += y[1]

            c_ans = str(c_ans)
            ans = str(ans)

            percent = f"{x.percentage()}%"
            percentages.append(x.percentage())

            last_date = x.last_date

            contents.append([subject, c_ans, ans, percent, last_date])

        pdf = PDF()
        pdf.setFooter(f"""Generated by {self.name} at {datetime.now().strftime('%H:%M %a, %d %B %Y')}
                This is an automatically generated report and therefore, does not require a signature.""")
        pdf.add_page()
        pdf.set_font("Times", 'B', 20)
        pdf.write(0, "Score Report")
        pdf.ln(5)
        pdf.set_font("Times", size=14)
        pdf.write(15, f"Student Name: {student_name}")
        pdf.ln()
        pdf.write(0, f"Class: {student_class}")
        pdf.ln(5)
        pdf.create_table(table_data=contents, data_size=14, align_data="C", align_header="C", cell_width="uneven", x_start="C")
        pdf.ln()
        pdf.write(0, f"Overall Percentage: {numpy.mean(percentages).round(2)}%")
        pdf.ln()
        # pdf.write(15, f"Generated by {self.name} at {datetime.now().strftime('%H:%M %a, %d %B %Y')}")
        pdf.output(f"{student_name}'s Score Report.pdf")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    StartupWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupStartup(StartupWindow)
    StartupWindow.showMaximized()
    sys.exit(app.exec_())
