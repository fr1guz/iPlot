import os
import sys
import sqlite3

from PyQt6.QtWidgets import (QMainWindow, QInputDialog, QMessageBox, 
                             QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton)

from .HistoryWindow import HistoryWindow

from ..PlotWidget import PlotWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.conn = self.initDatabases()
        self.currentUserId = self.initUser()

        self.history_window = HistoryWindow(self.conn, self.currentUserId)

        self.initUi()
        self.connectUi()
    
    def initDatabases(self) -> sqlite3.Connection:
        if os.name == "nt":
            path = os.path.expanduser("~\\Documents")
            sep = os.path.expanduser("\\")
        else:
            path = os.path.expanduser("~/Documents")
            sep = "/"
        
        if not os.path.isdir(f"{path}{sep}iPlot"):
            os.mkdir(f"{path}{sep}iPlot")

        if not os.path.isfile(f"{path}{sep}iPlot{sep}plot.sqlite3"):
            open(f"{path}{sep}iPlot{sep}plot.sqlite3", "w").close()
        
        conn = sqlite3.connect(f"{path}{sep}iPlot{sep}plot.sqlite3")
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

        conn.commit()

        return conn

    def initUser(self) -> int:
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
                            return cur.execute(f"SELECT MAX(id) FROM users").fetchone()[0]

                if button == QMessageBox.StandardButton.Cancel:
                    sys.exit(0)
        
    def initUi(self) -> None:
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

    def connectUi(self) -> None:
        self.plotButton.clicked.connect(lambda: self.plotWidget.plot(self.logg(self.enterFunction.text())))
        self.clearButton.clicked.connect(self.clear)
        self.showHist.clicked.connect(self.history_window.show)

    def clear(self) -> None:
        self.plotWidget.figure.clear()
        self.plotWidget.canvas.draw()
    
    def logg(self, expression: str) -> str:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO history(user_id, func, time) VALUES (?, ?, datetime('now'))", (self.currentUserId, expression))
        self.conn.commit()
        return expression