import os

import numpy as np
from PySide import QtGui
from PySide.QtCore import Signal
from PySide.QtGui import (QImage, QPixmap, QWidget, QMainWindow, QFileDialog,
                          QPainter, QBrush, QColor)

from ui.ui_image_window import Ui_ImageWindow
from ui.widgets.noise_dialog import NoiseDialog
from utils import array_to_image, image_to_array, fft_to_array, array_to_fft



class ImageWidget(QMainWindow, Ui_ImageWindow):
    image_updated = Signal(np.ndarray, str)

    histogram = None
    fourier = None

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setup_actions()


    def setup_actions(self):
        self.action_save.triggered.connect(self.save)
        self.action_save_as.triggered.connect(self.save_as)
        self.action_add_noise.triggered.connect(self.add_noise)


    def save(self):
        pass

    def save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save As")
        self.image_label.pixmap().save(path)

    def add_noise(self):
        dialog = NoiseDialog()
        if not dialog.exec_():
            return
        function = dialog.painter_function

        image = self.image_label.pixmap().toImage()
        painter = QPainter(image)
        function(painter, QColor(0, 0, 0))
        self.update(image_to_array(image))
        del painter



    def update(self, image_array, refresh=True, cause='load'):

        self.image_array = image_array.copy()
        self.image_updated.emit(image_array.copy(), cause)

        if refresh:
            image = array_to_image(self.image_array)
            self.image_label.setPixmap(QPixmap(image))

    def from_fourier(self, fft_array):
        #print(fft_array)
        self.update(fft_array, cause='fourier')

    def setup_menu(self):
        self.menu = QtGui.QMenu()
        self.menu.addAction(QtGui.QAction("item", self))

    def show_context_menu(self, point):
        self.menu.popup(point)

    def load_file(self, file_name):
        array = image_to_array(QImage(file_name), to_gray=True)
        self.update(array)
        self.setWindowTitle(os.path.basename(file_name))
