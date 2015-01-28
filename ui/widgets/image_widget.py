import os

import numpy as np
from PySide import QtGui
from PySide.QtCore import Signal
from PySide.QtGui import (QImage, QPixmap, QWidget)

from ui.ui_image_window import Ui_ImageWindow
from utils import array_to_image, image_to_array, fft_to_array, array_to_fft



class ImageWidget(QWidget, Ui_ImageWindow):
    image_updated = Signal(np.ndarray, str)

    histogram = None
    fourier = None

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

    def update(self, image_array, function=None, refresh=True, cause='load'):
        if function:
            function(image_array)

        # TESTING ROUTINE
        #self.image_array = fft_to_array(array_to_fft(image_array.copy()))

        self.image_array = image_array.copy()
        self.image_updated.emit(image_array.copy(), cause)

        if refresh:
            image = array_to_image(self.image_array)
            self.image_label.setPixmap(QPixmap(image))

    def from_fourier(self, fft_array):
        #print(fft_array)
        self.update(fft_to_array(fft_array), cause='fourier')

    def setup_menu(self):
        self.menu = QtGui.QMenu()
        self.menu.addAction(QtGui.QAction("item", self))

    def show_context_menu(self, point):
        self.menu.popup(point)

    def load_file(self, file_name):
        array = image_to_array(QImage(file_name), to_gray=True)
        self.update(array)
        self.setWindowTitle(os.path.basename(file_name))
