import socket
import sys
import pickle
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import PyQt5.QtCore as qtc
import mysql.connector
import time


class StudentWindow(qtw.QWidget):
    success = qtc.pyqtSignal()
    # client = Client_()

    def __init__(self, Client):
        super().__init__()
        self.setWindowTitle("Quiz GUI")
        self.client = Client

        form_layout = qtw.QFormLayout()
        self.setLayout(form_layout)

        self.login_label = qtw.QLabel("Student Login")
        self.login_label.setFont(qtg.QFont("Times New Roman", 24))
        self.login_label.setAlignment(qtc.Qt.AlignCenter)

        # self.name = qtw.QLineEdit(self)
        self.password = qtw.QLineEdit(self)
        self.password.setFont(qtg.QFont("Times New Roman", 16))

        self.username = qtw.QLineEdit(self)
        self.username.setFont(qtg.QFont("Times New Roman", 16))

        self.submit_btn = qtw.QPushButton("Submit")
        self.submit_btn.clicked.connect(self.submit)
        self.submit_btn.setFont(qtg.QFont("Times New Roman", 20))

        self.output = qtw.QLabel(self)
        self.output.setFont(qtg.QFont("Times New Roman", 16))

        form_layout.addRow(self.login_label)
        form_layout.addRow("Email: ", self.username)
        form_layout.addRow("Password: ", self.password)
        form_layout.addRow(self.submit_btn)
        form_layout.addRow("Output: ", self.output)

    # self.show()

    def check_name(self, name):
        select = self.client.query_sql("SELECT email FROM students", ())
        names = []
        for x in select:
            select_name = x[0]
            names.append(select_name)
        # print(name)
        if name in names:
            return True
        else:
            return False

    def submit(self):
        Name = self.username.text()
        password = self.password.text()

        name_status = self.check_name(Name)
        # print(name_status)

        if not name_status:
            self.output.setText("Login Failed! Incorrect email.")
            return
        else:
            pass
        select = self.client.query_sql(f"SELECT password FROM students WHERE email = %s", (Name,))
        for x in select:
            out_put = x
        pass_word = out_put[0]

        if password == pass_word:
            self.output.setText("Login Successful!")
            select = self.client.query_sql(f"SELECT name, class, student_id FROM students WHERE email = %s", (Name,))
            for x in select:
                self.final_name = x[0]
                self.grade = x[1]
                self.student_id = x[2]
            # print(self.grade)
            self.success.emit()
            # print("Done")
            # self.client.disconnect()
            self.close()

        elif len(password) == 0:
            self.output.setText("Please enter your password.")

        elif password != pass_word:
            self.output.setText("Login Failed! Incorrect password.")


'''
app = qtw.QApplication([])
mw = StudentWindow()
mw.show()

app.exec()
'''
