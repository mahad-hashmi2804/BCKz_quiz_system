import sys
import socket
import pickle
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import mysql.connector
import time


class TeacherWindow(qtw.QWidget):
    success = qtc.pyqtSignal()

    # client = Client_()

    def __init__(self, Client):
        super().__init__()
        self.setWindowTitle("Quiz GUI")
        self.client = Client

        self.form_layout = qtw.QFormLayout()
        self.setLayout(self.form_layout)
        # self.form_layout.setGeometry(qtc.QRect(100, 100, 1000, 244))
        # self.form_layout.setFont(qtg.QFont("Times New Roman", 14))

        self.login_label = qtw.QLabel("Login")
        self.login_label.setFont(qtg.QFont("Times New Roman", 24))
        self.login_label.setAlignment(qtc.Qt.AlignCenter)
        # self.name = qtw.QLineEdit(self)
        self.password = qtw.QLineEdit(self)
        self.password.setFont(qtg.QFont("Times New Roman", 14))
        # self.password.setStyleSheet("lineedit-password-character: 9679;")

        self.username = qtw.QComboBox(self)
        self.username.setFont(qtg.QFont("Times New Roman", 14))
        self.grab_names()

        self.submit_button = qtw.QPushButton("Submit")
        self.submit_button.setFont(qtg.QFont("Times New Roman", 20))
        self.submit_button.clicked.connect(self.submit)

        self.output = qtw.QLabel(self)
        self.output.setFont(qtg.QFont("Times New Roman", 16))

        self.form_layout.addRow(self.login_label)
        self.form_layout.addRow("Name: ", self.username)
        self.form_layout.addRow("Password: ", self.password)
        self.form_layout.addRow(self.submit_button)
        self.form_layout.addRow("Output: ", self.output)

        ##app.aboutToQuit.connect(self.client.disconnect)

    # self.success.connect(MainWindow.success_teacher)

    # self.show()

    def grab_names(self):
        select = self.client.query_sql("SELECT name, subject, teacher_id FROM teachers", ())
        for x in select:
            name = x[0]
            subject = x[1]
            ID = x[2]
            self.username.addItem(f"{name} - {subject}", ID)

    def submit(self):
        ID = self.username.currentData()
        password = self.password.text()

        select = self.client.query_sql("SELECT email, password FROM teachers WHERE teacher_id = %s", (ID,))
        for x in select:
            out_put = x
        email = out_put[0]
        pass_word = out_put[1]

        if password == pass_word:
            self.output.setText("Login Successful!")
            self.success.emit()
            self.close()

        elif len(password) == 0:
            self.output.setText("Please enter your password.")

        elif password != pass_word:
            self.output.setText("Login Failed! Incorrect password.")

'''
myclient = Client_()

app = qtw.QApplication([])
mw = TeacherWindow(myclient)
mw.show()

app.exec()
'''