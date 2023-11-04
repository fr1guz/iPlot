import os
import sqlite3
import csv

from PyQt6.QtWidgets import QMainWindow, QTableWidgetItem, QFileDialog

from .Ui.history_window_ui import Ui_HistoryWindow


class HistoryWindow(QMainWindow, Ui_HistoryWindow):
    def __init__(self, conn: sqlite3.Connection, user_id: int) -> None:
        super().__init__()

        self.currentUserId = user_id
        self.conn = conn

        self.setupUi(self)
        self.initUI()
        self.connectUI()
    
    def initUI(self) -> None:
        res = self.conn.cursor().execute(f"SELECT * FROM history INNER JOIN users ON history.user_id = users.id WHERE history.user_id = {self.currentUserId}").fetchall()
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(("id", "user_id", "func", "time"))
        self.tableWidget.setRowCount(0)

        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

    def connectUI(self) -> None:
        self.exportCSV.clicked.connect(self.saveSCV)

    def saveSCV(self) -> None:
        path, ok_pressed = QFileDialog().getSaveFileName(self, "Save File", "/home/j4dzg3r/Documents/untitled.csv", "(*.csv)")
        if ok_pressed:
            cur = self.conn.cursor()
            cur.execute(f"SELECT * FROM history INNER JOIN users ON history.user_id = users.id WHERE history.user_id = {self.currentUserId}")
            with open(path, "w") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([i[0] for i in cur.description])
                csv_writer.writerows(cur)
    
    def showHist(self):
        self.initUI()
        self.show()
