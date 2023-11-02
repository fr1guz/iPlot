import sqlite3
import sys
import os
import random
from PyQt6 import QtCore

import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, 
                             QHBoxLayout, QMainWindow, 
                             QPushButton, QApplication,
                             QLineEdit, QInputDialog, QMessageBox)


class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.initUi()

    def initUi(self):
        self.mainLayout = QVBoxLayout(self)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.navToolbar = NavigationToolbar(self.canvas, self)

        self.mainLayout.addWidget(self.canvas)
        self.mainLayout.addWidget(self.navToolbar)
    
    def plot(self, expression: str):
        x = np.linspace(-20, 20, 500)
        y = np.array([eval(expression.replace("X", f"{i}")) for i in x])
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.axhline(y=0, xmin=-10.25, xmax=10.25, color="#000000")
        ax.axvline(x=0, ymin=-2, ymax=2, color="#000000")
        
        ax.plot(x, y)
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.conn = self.initDatabases()
        self.currentUserId = self.initUser()

        self.initUi()
        self.connectUi()
    
    def initDatabases(self):
        if not os.path.isfile("/home/j4dzg3r/Documents/calendown.sqlite3"):
            os.mknod("/home/j4dzg3r/Documents/calendown.sqlite3")
        
        conn = sqlite3.connect("/home/j4dzg3r/Documents/calendown.sqlite3")
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS users (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    login text NOT NULL,
                    password text,
                    last_entry text NOT NULL
        );""")

        cur.execute("""CREATE TABLE IF NOT EXISTS history (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    user_id integer NOT NULL,
                    func text NOT NULL,
                    time text NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
        );""")

        return conn

    def initUser(self):
        while True:
            login, ok_pressed = QInputDialog.getText(self, "Инициализация", "Введи логин (если тебя нет, зарегистрируем)")
            if ok_pressed is False:
                sys.exit(0)
            cur = self.conn.cursor()
            user = cur.execute(f"SELECT * FROM users WHERE login = '{login}'").fetchone()
            if user:
                while True:
                    password, ok_pressed = QInputDialog().getText(self, "Пароль", "Введи пароль")
                    
                    if ok_pressed:
                        if user[2] == password:
                            cur.execute(f"UPDATE users SET last_entry = datetime('now') WHERE id = {user[0]}")
                            self.conn.commit()
                            return user[0]
                    else:
                        sys.exit(0)
            else:
                dlg = QMessageBox(self)
                dlg.addButton(QMessageBox.StandardButton.Yes)
                dlg.addButton(QMessageBox.StandardButton.No)
                dlg.addButton(QMessageBox.StandardButton.Cancel)
                dlg.setWindowTitle("Something goes wrong")
                dlg.setText("Я тебя не нашел. Ты зарегистрирован? Может хочешь уйти от ответа?")
                button = dlg.exec()

                done = False

                if button == QMessageBox.StandardButton.No:
                    while True:
                        password, _ = QInputDialog.getText(self, "Пароль", "Твой логин у меня уже есть. Введи пароль")
                        if not password:
                            dlg = QMessageBox(self)
                            dlg.addButton(QMessageBox.StandardButton.Ok)
                            dlg.addButton(QMessageBox.StandardButton.Cancel)
                            dlg.setText("Введи нормальный пароль.")
                            button = dlg.exec()

                            if button == QMessageBox.StandardButton.Cancel:
                                sys.exit(0)
                        else:
                            cur.execute(f"INSERT INTO users (login, password, last_entry) VALUES ('{login}', '{password}', datetime('now'))")
                            self.conn.commit()
                            done = True
                            break
                
                if done:
                    break

                if button == QMessageBox.StandardButton.Cancel:
                    sys.exit(0)
        
    def initUi(self):
        self.myCentralWidget = QWidget(self)
        self.vertLabel = QVBoxLayout(self.myCentralWidget)
        self.horLabel = QHBoxLayout(self.myCentralWidget)

        self.plotWidget = PlotWidget()

        self.enterFunction = QLineEdit(self)
        self.plotButton = QPushButton("Plot")
        self.clearButton = QPushButton("Clear")
        self.showHist = QPushButton("Show history", self)

        self.horLabel.addWidget(self.plotButton)
        self.horLabel.addWidget(self.clearButton)

        self.vertLabel.addWidget(self.enterFunction)
        self.vertLabel.addLayout(self.horLabel)
        self.vertLabel.addWidget(self.plotWidget)
        self.vertLabel.addWidget(self.showHist)

        self.setCentralWidget(self.myCentralWidget)

    def connectUi(self):
        self.plotButton.clicked.connect(lambda: self.plotWidget.plot(self.enterFunction.text()))
        self.clearButton.clicked.connect(self.clear)

    def clear(self):
        self.plotWidget.figure.clear()
        self.plotWidget.canvas.draw()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = MainWindow()
    p.show()
    sys.exit(app.exec())

