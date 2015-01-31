from PySide import QtGui
from PySide.QtGui import (QMdiSubWindow, QMainWindow, QImage, QPixmap, QSlider,
                          QWidget, qRgb, QLabel, QSpinBox, QPainter, QDialog,
                          QComboBox, QCheckBox, QFileDialog)

from PySide.QtCore import Qt, Signal, Slot
import numpy as np

from ui.ui_fourier_window import Ui_FourierWindow
import ui.ui_fourier_filter as ff
import ui.ui_fourier_resize as fr
from ui.widgets.color_widget import ColorWidget
from common import brush_shapes


class ResizeDialog(QDialog, fr.Ui_Dialog):
    resized = Signal(float)

    def __init__(self, accept=None, reject=None, low=True, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self._resize)

    def _resize(self):
        self.resized.emit(self.doubleSpinBox.value())
        self.close()


class PassFilterDialog(QDialog, ff.Ui_Dialog):
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
        self.mask = round_mask(diameter, self.width, self.height, low=self.low)
        self.updated.emit(self.mask.copy())

    def _clear(self):
        self.updated.emit(np.zeros((self.height, self.width)))
        self.hide()

    def closeEvent(self, event):
        self._clear()
        QDialog.closeEvent(self, event)

    def _apply_mask(self):
        if self.mask is not None:
            self.mask_accepted.emit(self.mask.copy())
        self._clear()

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
        self.resize(800, 600)

    def setup_actions(self):
        self.action_low_pass.triggered.connect(self.on_action_low_pass)
        self.action_high_pass.triggered.connect(self.on_action_high_pass)
        self.action_resize.triggered.connect(self.on_action_resize)
        self.action_save_as.triggered.connect(self.on_action_save_as)

        self.action_restore.triggered.connect(self.fourier.on_restore)
        self.action_update.triggered.connect(self.fourier.regen_image)

    def on_action_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self)
        if not path:
            return
        self.fourier.image.save(path)

    def setup_toolbar(self):
        color_widget = ColorWidget()
        color_widget.color_changed.connect(self.fourier.on_color_change)
        self.toolBar.addWidget(color_widget)

        self.toolBar.addWidget(QLabel("Shape:"))
        size_spin = QSpinBox(self.toolBar)
        size_spin.setValue(20)
        size_spin.valueChanged[int].connect(self.fourier.on_size_change)

        shape_combo = QComboBox(self.toolBar)
        shape_combo.activated[str].connect(self.fourier.on_shape_change)
        shape_combo.addItems(brush_shapes)

        self.toolBar.addWidget(shape_combo)
        self.toolBar.addWidget(size_spin)

        self.toolBar.addWidget(QLabel("X Symmetry"))
        x_sym = QCheckBox(self.toolBar)
        x_sym.toggled.connect(self.fourier.on_x_toggle)
        self.toolBar.addWidget(x_sym)

        self.toolBar.addWidget(QLabel("Y Symmetry"))
        y_sym = QCheckBox(self.toolBar)
        y_sym.toggled.connect(self.fourier.on_y_toggle)
        self.toolBar.addWidget(y_sym)

    def update_fourier(self, image_array, cause):
        flush = False
        if cause == 'fourier':
            return
        if cause == 'load':
            flush = True

        self.fourier.update_fourier(image_array, flush=flush)

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

    def on_action_resize(self):
        self.r_dialog = ResizeDialog()
        self.r_dialog.resized.connect(self.fourier.on_resize)
        self.r_dialog.show()
