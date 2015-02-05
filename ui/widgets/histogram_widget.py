from PySide import QtGui
from PySide.QtGui import QWidget
from PySide.QtCore import Signal
import numpy as np

from ui.ui_histogram_window import Ui_HistogramWindow


class HistogramWidget(QWidget, Ui_HistogramWindow):
    fourier_updated = Signal(np.ndarray)

    def __init__(self, parent_title, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle("{}'s Histogram".format(parent_title))

    def update_histogram(self, image_array, cause):
        self.histogram.update(image_array)
