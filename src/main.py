import sys

from PyQt6.QtWidgets import QApplication

from widgets.windows.MainWindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    p = MainWindow()
    p.show()
    sys.exit(app.exec())