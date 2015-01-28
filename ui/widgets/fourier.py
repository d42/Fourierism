
import numpy as np
from PySide.QtGui import QWidget, QPixmap, QPainter, QImage, QCursor, QColor, QDialog, QGraphicsOpacityEffect
from PySide.QtCore import Qt, Signal, Slot, QRect

from ui.widgets.color_widget import ColorWidget
from utils import (array_to_image, image_to_array, rescale_array,
                   array_to_fft, fft_to_array)


from itertools import product
import matplotlib.pyplot as plt
import logging


class Overlay(QWidget):
    mask = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPalette(Qt.transparent)
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(0.5)
        self.setGraphicsEffect(self.effect)

    def paintEvent(self, event):
        if self.mask is None:
            return

        h, w = self.mask.shape
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.red)

        for x, y in product(range(w), range(h)):
            if self.mask[y][x]:
                painter.drawPoint(x, y)

    @Slot()
    def clear(self):
        self.set(np.zeros((self.height(), self.width())))

    @Slot(np.ndarray)
    def set(self, mask):
        self.mask = mask
        self.update()


class Fourier(QWidget):

    fourier_updated = Signal(np.ndarray)
    image = None
    pressed = False
    scale_factor = None
    color = QColor(0, 0, 0)
    # signal fourier updated

    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_cursor('square', 20)
        self.overlay = Overlay(self)

    def emit_fourier(self):
        fc = self.raw_fourier.copy()

    def update_image(self, fft_array, factor=None):
        logging.info("updating fourier image")
        self.scale_factor = factor or np.max(fft_array.flat)
        scaled_values = rescale_array(fft_array, self.scale_factor)
        self.image = array_to_image(scaled_values, real=True)
        self.overlay.resize(self.image.size())

    def update_fourier(self, image_array):
        logging.info("updating raw fourier")
        self.raw_fourier = array_to_fft(image_array)
        self.update_image(self.raw_fourier)
        #self.on_action_low_pass()
        # plt.imshow(self.raw_fourier.astype(np.ubyte))
        # plt.show()

    def update_cursor(self, shape, size):
        self.cursor_size = size

        cursor_pix = QPixmap(size, size)
        cursor_pix.fill(Qt.transparent)

        painter = QPainter(cursor_pix)
        painter.setPen(QColor(255, 0, 0))

        if shape == 'circle':
            painter.drawEllipse(0, 0, size-1, size-1)
        elif shape == 'square':
            painter.drawRect(0, 0, size-1, size-1)

        del painter

        cursor = QCursor(cursor_pix, 0, 0)
        self.setCursor(cursor)

    def on_size_change(self, size):
        """ Brush size changed """
        self.size = size
        self.update_cursor(self.shape, self.size)

    def on_shape_change(self, shape):
        """ Brush shape changed """
        self.shape = shape
        self.update_cursor(self.shape, self.size)

    def draw_mask_on_fourier(self, mask, value=0x00):
        self.raw_fourier[mask] = value
        self.update_image(self.raw_fourier, self.scale_factor)
        self.fourier_updated.emit(self.raw_fourier.copy())

    def paintEvent(self, event):
        """ Paint widget as self.image content """
        if not self.image:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        rect = event.rect()
        painter.drawImage(rect.topLeft(), self.image, rect)

    def mousePressEvent(self, event):
        self.pressed = True
        self.draw_buffer = np.empty(self.raw_fourier.shape)
        self.draw_buffer.fill(-1)
        self.draw(event)

    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.draw(event)
        self.fourier_draw()

    def mouseMoveEvent(self, event):
        if self.pressed:
            self.draw(event)

    def fourier_draw(self):
        values = (self.draw_buffer[self.draw_buffer != -1]/255) * self.scale_factor
        self.raw_fourier[self.draw_buffer != -1] = values
        self.fourier_updated.emit(self.raw_fourier.copy())

    def draw(self, event):
        x, y = event.x(), event.y()
        rect = QRect(x, y, self.cursor_size - 1, self.cursor_size - 1)
        painter = QPainter(self.image)

        painter.fillRect(rect, self.color)
        del painter
        self.update()

        cs = self.cursor_size
        self.draw_buffer[y:y+cs, x:x+cs] = self.color.red()

    def sizeHint(self):
        if not self.image:
            return super().minimumSizeHint()

        return self.image.size()
