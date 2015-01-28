import PySide
import pyqtgraph as pg

from PySide import QtGui, QtCore
import numpy as np


class Histogram(pg.PlotWidget):
    bp = None

    def __init__(self, parent=None):
        super().__init__(name="Histogram")
        self.parent = parent
        self.setYRange(0, 1)
        self.setXRange(0, 255)
        self.pl = self.plot()
        self.hideAxis('left')
        self.hideAxis('bottom')
        self.setMouseEnabled(False, False)
        self.bp = pg.BarGraphItem(x=np.arange(256), width=0.5,
                                  height=[0]*256)
        self.addItem(self.bp)

    def update(self, image_array):
        """:type image_array: numpy.ndarray """
        h, w = image_array.shape
        total = h * w
        values = np.bincount(image_array.flat, minlength=256)/total
        self.values = values
        self.bp.setOpts(x=np.arange(256), width=0.5, height=values)
