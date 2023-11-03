# import sqlite3
# import sys
# import os
# import csv
# from PyQt6 import QtCore

# import numpy as np
# import numpy.typing as npt

# from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure

# from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
#                              QMainWindow, QPushButton, QApplication,
#                              QLineEdit, QInputDialog, QMessageBox,
#                              QFileDialog, QTableWidgetItem)

# from src.widgets.windows.Ui.history_window_ui import Ui_HistoryWindow


# class UnbalancedExpressionError(Exception):
#     pass


# class CalulateError(Exception):
#     pass


# class Calculator:
#     def __init__(self) -> None:
#         self.OPERATORS = "+-*/^"
#         self.FUNC_KEYWORD = "func"
#         self.FUNCTIONS = {"cos": np.cos, "sin": np.sin, "tg": np.tan, "ctg": lambda x: 1 / np.tan(x)}
#         self.OPEN_BRACKET = "("
#         self.CLOSED_BRACKET = ")"
#         self.BREAK = "?"
#         self.SEPARATOR = "."
#         self.stackNumbers: list[np.float64] = []
#         self.stackOperators: list[str] = []
#         self.stackRPN: list[str] = []
    
#         self.enum_modifiers: dict[str, int] = {
#             self.BREAK: 0,
#             self.OPERATORS[0]: 1,
#             self.OPERATORS[1]: 2,
#             self.OPERATORS[2]: 3,
#             self.OPERATORS[3]: 4,
#             self.OPERATORS[4]: 5,
#             self.FUNC_KEYWORD: 6,
#             self.OPEN_BRACKET: 7,
#             self.CLOSED_BRACKET: 8
#         }

#         self.priority: list[list[int]] = [
#             [4, 1, 1, 1, 1, 1, 1, 1, 5],
#             [2, 2, 2, 1, 1, 1, 1, 1, 2],
#             [2, 2, 2, 1, 1, 1, 1, 1, 2],
#             [2, 2, 2, 2, 2, 1, 1, 1, 2],
#             [2, 2, 2, 2, 2, 1, 1, 1, 2],
#             [2, 2, 2, 2, 2, 2, 1, 1, 2],
#             [2, 2, 2, 2, 2, 2, 1, 1, 2],
#             [5, 1, 1, 1, 1, 1, 1, 1, 3]
#         ]
    
#     def stringSplit(self, expression: str) -> list[str]:
#         expression = expression.replace(" ", "").replace("(-", "(0-").replace(f"{self.SEPARATOR}-", f"{self.SEPARATOR}0-")
#         if expression[0] == '-':
#             expression = "0" + expression

#         extra = ""

#         result: list[str] = []

#         for i in expression:
#             if i in self.OPERATORS or i == self.CLOSED_BRACKET or i == self.OPEN_BRACKET:
#                 if extra:
#                     result.append(extra)
#                     extra = ""
#                 result.append(i)
#             else:
#                 extra += i

#         if extra:
#             result.append(extra)

#         result.append(self.BREAK)
#         return result
    
#     def isNumber(self, item: str) -> bool:
#         try:
#             float(item)
#         except ValueError:
#             return False
#         return True

#     def listToRPN(self, arr: list[str]) -> None:
#         self.stackRPN.clear()
#         self.stackOperators.clear()
#         self.stackOperators.append(self.BREAK)

#         for item in arr:
#             if self.isNumber(item):
#                 self.stackRPN.append(item)
#             else:
#                 while True:
#                     currentItem = item if item not in self.FUNCTIONS else self.FUNC_KEYWORD
#                     previousItem = self.stackOperators[-1] if self.stackOperators[-1] not in self.FUNCTIONS else self.FUNC_KEYWORD
#                     whatToDo = self.priority[self.enum_modifiers[previousItem]][self.enum_modifiers[currentItem]]

#                     if whatToDo == 1:
#                         self.stackOperators.append(item)
#                         break
#                     elif whatToDo == 2:
#                         self.stackRPN.append(self.stackOperators.pop())
#                     elif whatToDo == 3:
#                         self.stackOperators.pop()
#                         break
#                     elif whatToDo == 4:
#                         return
#                     else:
#                         raise UnbalancedExpressionError("Проверьте скобки")
                    
    
#     def calculate(self, expression: str) -> np.float64 | float:
#         self.listToRPN(self.stringSplit(expression))
#         self.stackNumbers.clear()
#         for item in self.stackRPN:
#             if self.isNumber(item):
#                 self.stackNumbers.append(np.float64(float(item)))
#             else:
#                 try:
#                     val2 = self.stackNumbers.pop()
#                     val1 = 0
#                     if item in self.OPERATORS:
#                         val1 = self.stackNumbers.pop()
#                 except IndexError:
#                     raise IndexError
#                 if item == "+":
#                     self.stackNumbers.append(val1 + val2)
#                 elif item == "-":
#                     self.stackNumbers.append(val1 - val2)
#                 elif item == "*":
#                     self.stackNumbers.append(val1 * val2)
#                 elif item == "/":
#                     res = val1 / val2
#                     if res == np.inf:
#                         return np.inf
#                     self.stackNumbers.append(res)
#                 elif item == "^":
#                     self.stackNumbers.append(val1 ** val2)
#                 else:
#                     self.stackNumbers.append(self.FUNCTIONS[item](val2))

#         return self.stackNumbers[0]


# class PlotWidget(QWidget):
#     def __init__(self, parent: QWidget | None = None) -> None:
#         super().__init__(parent)
        
#         self.calc_class = Calculator()
#         self.initUi()

#     def initUi(self) -> None:
#         self.mainLayout = QVBoxLayout(self)

#         self.figure = Figure()
#         self.canvas = FigureCanvas(self.figure)
#         self.navToolbar = NavigationToolbar(self.canvas, self)

#         self.mainLayout.addWidget(self.canvas)
#         self.mainLayout.addWidget(self.navToolbar)
    
#     def plot(self, expression: str) -> None:
#         x = np.around(np.arange(-20, 20, 0.001), decimals=4)
#         y = np.array([self.calc_class.calculate(expression.replace("X", f"{i}")) for i in x], dtype=np.float64)
#         self.figure.clear()
#         ax = self.figure.add_subplot(111)

#         ax.axhline(y=0, xmin=-10.25, xmax=10.25, color="#000000")
#         ax.axvline(x=0, ymin=-2, ymax=2, color="#000000")
        
#         ax.plot(x, y)
#         self.canvas.draw()


# class HistoryWindow(QMainWindow, Ui_HistoryWindow):
#     def __init__(self, conn: sqlite3.Connection, user_id: int) -> None:
#         super().__init__()

#         self.currentUserId = user_id
#         self.conn = conn

#         self.setupUi(self)
#         self.initUI()
#         self.connectUI()
    
#     def initUI(self) -> None:
#         res = self.conn.cursor().execute(f"SELECT * FROM history INNER JOIN users ON history.user_id = users.id WHERE history.user_id = {self.currentUserId}").fetchall()
#         self.tableWidget.setColumnCount(4)
#         self.tableWidget.setRowCount(0)

#         for i, row in enumerate(res):
#             self.tableWidget.setRowCount(
#                 self.tableWidget.rowCount() + 1)
#             for j, elem in enumerate(row):
#                 self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

#     def connectUI(self) -> None:
#         self.exportCSV.clicked.connect(self.saveSCV)

#     def saveSCV(self) -> None:
#         path, ok_pressed = QFileDialog().getSaveFileName(self, "Save File", "/home/j4dzg3r/Documents/untitled.csv", "(*.csv)")
#         if ok_pressed:
#             cur = self.conn.cursor()
#             cur.execute(f"SELECT * FROM history INNER JOIN users ON history.user_id = users.id WHERE history.user_id = {self.currentUserId}")
#             with open(path, "w") as csv_file:
#                 csv_writer = csv.writer(csv_file)
#                 csv_writer.writerow([i[0] for i in cur.description])
#                 csv_writer.writerows(cur)


# class MainWindow(QMainWindow):
#     def __init__(self) -> None:
#         super().__init__()

#         self.conn = self.initDatabases()
#         self.currentUserId = self.initUser()

#         self.history_window = HistoryWindow(self.conn, self.currentUserId)

#         self.initUi()
#         self.connectUi()
    
#     def initDatabases(self) -> sqlite3.Connection:
#         if os.name == "nt":
#             path = os.path.expanduser("~\\Documents")
#             sep = os.path.expanduser("\\")
#         else:
#             path = os.path.expanduser("~/Documents")
#             sep = "/"
        
#         if not os.path.isdir(f"{path}{sep}iPlot"):
#             os.mkdir(f"{path}{sep}iPlot")

#         if not os.path.isfile(f"{path}{sep}iPlot{sep}plot.sqlite3"):
#             open(f"{path}{sep}iPlot{sep}plot.sqlite3", "w").close()
        
#         conn = sqlite3.connect(f"{path}{sep}iPlot{sep}plot.sqlite3")
#         cur = conn.cursor()

#         cur.execute("""CREATE TABLE IF NOT EXISTS users (
#                     id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
#                     login text NOT NULL,
#                     password text,
#                     last_entry text NOT NULL
#         );""")

#         cur.execute("""CREATE TABLE IF NOT EXISTS history (
#                     id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
#                     user_id integer NOT NULL,
#                     func text NOT NULL,
#                     time text NOT NULL,
#                     FOREIGN KEY (user_id) REFERENCES users (id)
#         );""")

#         conn.commit()

#         return conn

#     def initUser(self) -> int:
#         while True:
#             login, ok_pressed = QInputDialog.getText(self, "Инициализация", "Введи логин (если тебя нет, зарегистрируем)")
#             if ok_pressed is False:
#                 sys.exit(0)
#             cur = self.conn.cursor()
#             user = cur.execute(f"SELECT * FROM users WHERE login = '{login}'").fetchone()
#             if user:
#                 while True:
#                     password, ok_pressed = QInputDialog().getText(self, "Пароль", "Введи пароль")
                    
#                     if ok_pressed:
#                         if user[2] == password:
#                             cur.execute(f"UPDATE users SET last_entry = datetime('now') WHERE id = {user[0]}")
#                             self.conn.commit()
#                             return user[0]
#                     else:
#                         sys.exit(0)
#             else:
#                 dlg = QMessageBox(self)
#                 dlg.addButton(QMessageBox.StandardButton.Yes)
#                 dlg.addButton(QMessageBox.StandardButton.No)
#                 dlg.addButton(QMessageBox.StandardButton.Cancel)
#                 dlg.setWindowTitle("Something goes wrong")
#                 dlg.setText("Я тебя не нашел. Ты зарегистрирован? Может хочешь уйти от ответа?")
#                 button = dlg.exec()

#                 if button == QMessageBox.StandardButton.No:
#                     while True:
#                         password, _ = QInputDialog.getText(self, "Пароль", "Твой логин у меня уже есть. Введи пароль")
#                         if not password:
#                             dlg = QMessageBox(self)
#                             dlg.addButton(QMessageBox.StandardButton.Ok)
#                             dlg.addButton(QMessageBox.StandardButton.Cancel)
#                             dlg.setText("Введи нормальный пароль.")
#                             button = dlg.exec()

#                             if button == QMessageBox.StandardButton.Cancel:
#                                 sys.exit(0)
#                         else:
#                             cur.execute(f"INSERT INTO users (login, password, last_entry) VALUES ('{login}', '{password}', datetime('now'))")
#                             self.conn.commit()
#                             return cur.execute(f"SELECT MAX(id) FROM users").fetchone()[0]

#                 if button == QMessageBox.StandardButton.Cancel:
#                     sys.exit(0)
        
#     def initUi(self) -> None:
#         self.myCentralWidget = QWidget(self)
#         self.vertLabel = QVBoxLayout(self.myCentralWidget)
#         self.horLabel = QHBoxLayout(self.myCentralWidget)

#         self.plotWidget = PlotWidget()

#         self.enterFunction = QLineEdit(self)
#         self.plotButton = QPushButton("Plot")
#         self.clearButton = QPushButton("Clear")
#         self.showHist = QPushButton("Show history", self)

#         self.horLabel.addWidget(self.plotButton)
#         self.horLabel.addWidget(self.clearButton)

#         self.vertLabel.addWidget(self.enterFunction)
#         self.vertLabel.addLayout(self.horLabel)
#         self.vertLabel.addWidget(self.plotWidget)
#         self.vertLabel.addWidget(self.showHist)

#         self.setCentralWidget(self.myCentralWidget)

#     def connectUi(self) -> None:
#         self.plotButton.clicked.connect(lambda: self.plotWidget.plot(self.logg(self.enterFunction.text())))
#         self.clearButton.clicked.connect(self.clear)
#         self.showHist.clicked.connect(self.history_window.show)

#     def clear(self) -> None:
#         self.plotWidget.figure.clear()
#         self.plotWidget.canvas.draw()
    
#     def logg(self, expression: str) -> str:
#         cur = self.conn.cursor()
#         cur.execute("INSERT INTO history(user_id, func, time) VALUES (?, ?, datetime('now'))", (self.currentUserId, expression))
#         self.conn.commit()
#         return expression

import sys

from PyQt6.QtWidgets import QApplication

from widgets.windows.MainWindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = MainWindow()
    p.show()
    sys.exit(app.exec())