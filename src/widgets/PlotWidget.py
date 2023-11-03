from PyQt6.QtWidgets import QWidget, QVBoxLayout

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from .math.Calculator import Calculator

import numpy as np


class PlotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self.calc_class = Calculator()
        self.initUi()

    def initUi(self) -> None:
        self.mainLayout = QVBoxLayout(self)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.navToolbar = NavigationToolbar(self.canvas, self)

        self.mainLayout.addWidget(self.canvas)
        self.mainLayout.addWidget(self.navToolbar)
    
    def plot(self, expression: str) -> None:
        x = np.around(np.arange(-20, 20, 0.001), decimals=4)
        y = np.array([self.calc_class.calculate(expression.replace("X", f"{i}")) for i in x], dtype=np.float64)
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        ax.axhline(y=0, xmin=-10.25, xmax=10.25, color="#000000")
        ax.axvline(x=0, ymin=-2, ymax=2, color="#000000")
        
        ax.plot(x, y)
        self.canvas.draw()