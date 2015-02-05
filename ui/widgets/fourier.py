from itertools import product

from PySide.QtGui import (QWidget, QPixmap, QPainter, QImage, QCursor,
                          QColor, QGraphicsOpacityEffect)
from PySide.QtCore import Qt, Signal, Slot, QRect
from PySide.QtSvg import QSvgRenderer
import numpy as np


from ui.widgets.color_widget import ColorWidget
from utils import (array_to_image, image_to_array, rescale_array,
                   array_to_fft, fft_to_array, zeropad)

#magic_wand = QSvgRenderer(":cursors/magic_wand.svg")

class Overlay(QWidget):
    mask = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPalette(Qt.transparent)
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(0.5)
        self.setGraphicsEffect(self.effect)
        self.image = None

    def paintEvent(self, event):
        if self.image is None:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        rect = event.rect()
        painter.drawImage(rect.topLeft(), self.image, rect)

    @Slot()
    def clear(self):
        self.set(np.zeros((self.height(), self.width())))
        self.mask = None
        self.image = None

    @Slot(np.ndarray)
    def set(self, mask):
        self.mask = mask
        self.update()
        h, w = self.mask.shape

        colors = (self.mask.astype(np.uint32) * 0xffff0000)
        self.image = QImage(colors.tostring(), w, h, QImage.Format_ARGB32)


class Fourier(QWidget):
    """ Actual fourier display and drawing widget """

    fourier_updated = Signal(np.ndarray)
    image = None
    pressed = False
    scale_factor = None
    color = QColor(0, 0, 0)
    raw_fourier = None
    x_sym = False
    y_sym = False
    opp_sym = False
    # signal fourier updated

    def __init__(self, parent=None):
        super().__init__(parent)
        self.update_cursor('square', 20)
        self.overlay = Overlay(self)

    def update_image(self, fft_array, factor=None):

        scaled_values, sf = rescale_array(np.real(np.log2(fft_array)),
                                          self.scale_factor)
        self.scale_factor = sf
        self.image = array_to_image(scaled_values)
        self.setMinimumSize(self.image.size())
        self.overlay.resize(self.image.size())
        self.update()
        self.updateGeometry()
        # I have to deliver, and it's broken on windows.
        self.setMinimumSize(self.image.size())
        self.overlay.resize(self.image.size())
        self.update()
        self.updateGeometry()

    def update_fourier(self, image_array, flush=False):
        f = array_to_fft(image_array)
        if self.raw_fourier is None or flush:
            self.original = f.copy()

        self.raw_fourier = f.copy()

        self.update_image(self.raw_fourier)

    def update_cursor(self, shape, size):
        self.cursor_size = size
        self.shape = shape

        cursor_pix = QPixmap(size, size)
        cursor_pix.fill(Qt.transparent)

        painter = QPainter(cursor_pix)
        painter.setPen(QColor(255, 0, 0))

        if shape == 'circle':
            painter.drawEllipse(0, 0, size-1, size-1)
        elif shape == 'square':
            painter.drawRect(0, 0, size-1, size-1)
        elif shape == "magic wand":
            magic_wand.render(painter, QRect(0, 0, 20, 20))

        cursor = QCursor(cursor_pix, 0, 0)
        self.setCursor(cursor)
        del painter

    def on_size_change(self, size):
        """ Brush size changed """
        self.cursor_size = size
        self.update_cursor(self.shape, self.cursor_size)

    Slot(str)
    def on_shape_change(self, shape):
        """ Brush shape changed """
        self.shape = shape
        self.update_cursor(self.shape, self.cursor_size)

    def on_color_change(self, color):
        self.color = QColor(color, color, color)


    def emit_fourier(self):
        array = fft_to_array(self.raw_fourier)
        self.fourier_updated.emit(array)

    def on_restore(self):
        self.raw_fourier = self.original.copy()
        self.update_image(self.raw_fourier, self.scale_factor)
        #self.fourier_updated.emit(self.raw_fourier.copy())
        self.emit_fourier()

    def on_resize(self, factor):
        if factor == 1.0: return
        #even = lambda x: x if (x % 2 == 0) else x + 1
        array = self.raw_fourier

        reshape = lambda x_y: [int(factor * x_y[0]), int(factor * x_y[1])]
        diff = lambda x_y: [x_y[0] - array.shape[0], x_y[1] - array.shape[1]]
        nexteven = lambda x: x if (x % 2 == 0) else x + 1
        delta = map(nexteven, diff(reshape(array.shape)))
        newsize = tuple(x[0] + x[1] for x in zip(array.shape, delta))

        self.raw_fourier = zeropad(array, newsize)
        self.update_image(self.raw_fourier, self.scale_factor)
        #self.fourier_updated.emit(self.raw_fourier.copy())
        self.emit_fourier()

    def draw_mask_on_fourier(self, mask, value=0x00):
        self.raw_fourier[mask] = 2**value
        self.update_image(self.raw_fourier, self.scale_factor)
        self.emit_fourier()

    def regen_image(self):
        self.update_image(self.raw_fourier, self.scale_factor)

    def paintEvent(self, event):
        """ Paint widget as self.image content """
        if self.image is None:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        rect = event.rect()
        painter.drawImage(rect.topLeft(), self.image, rect)

    def mousePressEvent(self, event):
        self.pressed = True
        self.draw_buffer = QPixmap(self.image.size())
        color = self.color.red() ^ 0xAA
        self.draw_buffer.fill(QColor(color, color, color))
        self.draw(event)

    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.draw(event)
        self.fourier_draw()

    def mouseMoveEvent(self, event):
        if self.pressed:
            self.draw(event)

    def fourier_draw(self):

        arr = image_to_array(self.draw_buffer.toImage())

        values = arr[arr == self.color.red()] * (self.scale_factor/255)
        self.raw_fourier[arr == self.color.red()] = np.abs(2**values)
        self.emit_fourier()

    def _paint(self, painter, x, y):
        size = self.cursor_size
        shape = self.shape

        painter.setBrush(self.color)
        painter.setPen(Qt.NoPen)

        if shape == 'circle':
            painter.drawEllipse(x, y, size-1, size-1)
        elif shape == 'square':
            painter.drawRect(x, y, size-1, size-1)
        elif shape == "magic wand":
            magic_wand.render(painter, QRect(0, 0, 20, 20))

    def draw(self, event):
        x, y = event.x(), event.y()
        max_y, max_x = self.raw_fourier.shape

        for painter in map(QPainter, [self.image, self.draw_buffer]):
            self._paint(painter, x, y)
            if self.x_sym:
                self._paint(painter, abs(max_x - x - self.cursor_size), y)
            if self.y_sym:
                self._paint(painter, x, abs(max_y - y - self.cursor_size))
            if (self.x_sym and self.y_sym) or self.opp_sym:
                self._paint(painter, abs(max_x - x - self.cursor_size), abs(max_y - y - self.cursor_size))

            del painter

        self.update()

    def sizeHint(self):
        if not self.image:
            return super().minimumSizeHint()
        return self.image.size()

    def on_y_toggle(self, y_state):
        self.y_sym = y_state

    def on_x_toggle(self, x_state):
        self.x_sym = x_state

    def on_opp_toggle(self, opp_state):
        self.opp_sym = opp_state
