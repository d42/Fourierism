from PySide import QtGui
from PySide.QtGui import (QMdiSubWindow, QMainWindow, QImage, QPixmap, QSlider,
                          QWidget, qRgb, QLabel, QSpinBox, QPainter, QDialog)
from PySide.QtCore import Qt, Signal, Slot
import numpy as np

from ui.ui_fourier_window import Ui_FourierWindow
from ui.ui_fourier_filter import Ui_Dialog
from ui.widgets.color_widget import ColorWidget


class PassFilterDialog(QDialog, Ui_Dialog):
    mask_accepted = Signal(np.ndarray)
    updated = Signal(np.ndarray)
    mask = None

    def __init__(self, accept=None, reject=None, low=True, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.low = low
        self.horizontalSlider.valueChanged.connect(self.update_mask)
        if not reject:
            self.buttonBox.rejected.connect(self._clear)
        if not accept:
            self.buttonBox.accepted.connect(self._apply_mask)

    def setFourierSize(self, size):
        self.height = size.height()
        self.width = size.width()

    @Slot()
    def update_mask(self):
        max_dim = max(self.height, self.width)
        percent = self.horizontalSlider.value() / 100
        diameter = max_dim * percent
        self.mask = ~round_mask(diameter, self.width, self.height, low=self.low)
        self.updated.emit(self.mask.copy())

    def _clear(self):
        self.updated.emit(np.zeros((self.height, self.width)))
        self.hide()

    def closeEvent(self, event):
        QDialog.closeEvent(self, event)
        self._clear()

    def _apply_mask(self):
        if self.mask is not None:
            self.mask_accepted.emit(self.mask)

        self.close()


def round_mask(diameter, w, h, center=None, low=False):
    if not center:
        x = w // 2
        y = h // 2

    a, b = np.ogrid[-y:y, -x:x]
    if low:
        return a**2 + b**2 > diameter**2
    else:
        return a**2 + b**2 <= diameter**2


class FourierWidget(QMainWindow, Ui_FourierWindow):
    fourier_updated = Signal(np.ndarray)

    def __init__(self, parent_title):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setup_toolbar()
        self.setWindowTitle("{}'s Fourier".format(parent_title))
        self.fourier.fourier_updated.connect(self.fourier_updated.emit)

        self.setup_actions()

    def setup_actions(self):
        self.action_low_pass.triggered.connect(self.on_action_low_pass)
        self.action_high_pass.triggered.connect(self.on_action_high_pass)

    def setup_toolbar(self):
        self.toolBar.addWidget(ColorWidget())
        self.toolBar.addWidget(QLabel("papiesz"))
        self.color_spin = QSpinBox(self.toolBar)
        self.toolBar.addWidget(self.color_spin)

    def update_fourier(self, image_array, cause):
        if cause == 'fourier':
            return
        self.fourier.update_fourier(image_array)

    def on_action_low_pass(self):
        self.lp_dialog = PassFilterDialog()
        self.lp_dialog.setFourierSize(self.fourier.sizeHint())
        self.lp_dialog.updated.connect(self.fourier.overlay.set)
        self.lp_dialog.mask_accepted.connect(self.fourier.draw_mask_on_fourier)
        self.lp_dialog.show()

    def on_action_high_pass(self):
        self.hp_dialog = PassFilterDialog(low=False)
        self.hp_dialog.setFourierSize(self.fourier.sizeHint())
        self.hp_dialog.updated.connect(self.fourier.overlay.set)
        self.hp_dialog.mask_accepted.connect(self.fourier.draw_mask_on_fourier)
        self.hp_dialog.show()
