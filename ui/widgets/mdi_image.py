import os
from itertools import product

import numpy as np
from PySide import QtGui
from PySide.QtCore import Slot, Signal
from PySide.QtGui import (QMdiSubWindow, QImage, QPixmap, QWidget, qRgb)

import exceptions as e
from ui.ui_image_window import Ui_ImageWindow
from utils import image_to_array, array_to_image,  fft_to_array, rescale_array


class ImageWidget(QWidget, Ui_ImageWindow):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)


class MdiImage(QMdiSubWindow, Ui_ImageWindow):
    image_updated = Signal(np.ndarray)
    histogram = None
    fourier = None

    def from_fourier(self, fft_array):
        pass
        #gnuj = fft_to_array(fft_array)
        #import ipdb; ipdb.set_trace()

    def setup_menu(self):
        self.menu = QtGui.QMenu()
        self.menu.addAction(QtGui.QAction("item", self))

    def show_context_menu(self, point):
        self.menu.popup(point)

    def load_file(self, file_name):
        array = image_to_array(QImage(file_name), to_gray=True)
        self.update(array)
        self.setWindowTitle(os.path.basename(file_name))
