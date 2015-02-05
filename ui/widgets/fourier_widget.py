from PySide import QtGui
from PySide.QtGui import (QMainWindow, QSlider,
                          QLabel, QSpinBox, QDialog,
                          QComboBox, QCheckBox, QFileDialog)

from PySide.QtCore import Signal, Slot
import numpy as np

from ui.ui_fourier_window import Ui_FourierWindow

import ui.ui_fourier_filter as ff
import ui.ui_fourier_resize as fr
import ui.ui_fourier_band as bd

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


class Dialog:

    def setFourierSize(self, size):
        self.height = size.height()
        self.width = size.width()

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

    def reject(self):
        self._clear()


class BandpassDialog(Dialog, QDialog, bd.Ui_Dialog):
    mask_accepted = Signal(np.ndarray)
    updated = Signal(np.ndarray)

    def __init__(self, low=True, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)


        def bind_slider(check, action):
            def inner(x):
                if check(x):
                    action(x)
            return inner


        bind1 = bind_slider(lambda x: self.slider_from.value() > x,
                            lambda x: self.slider_from.setValue(max(0, x-1)))

        bind2 = bind_slider(lambda x: self.slider_to.value() < x,
                            lambda x: self.slider_to.setValue(min(100, x+1)))
        
        self.slider_to.valueChanged.connect(bind1)
        self.slider_from.valueChanged.connect(bind2)

        self.slider_to.valueChanged.connect(self.update_mask)
        self.slider_from.valueChanged.connect(self.update_mask)
        self.check_inverse.stateChanged.connect(self.update_mask)

        self.buttonBox.rejected.connect(self._clear)
        self.buttonBox.accepted.connect(self._apply_mask)

    @Slot()
    def update_mask(self):
        max_dim = max(self.height, self.width)
        inverse = self.check_inverse.isChecked()

        diam1 = max_dim * (self.slider_from.value() / 100)
        diam2 = max_dim * (self.slider_to.value() / 100)

        self.mask = self._gen_mask(diam1, diam2, inverse)
        self.updated.emit(self.mask.copy())

    def _gen_mask(self, diam1, diam2, inverse):
        x = self.width // 2
        y = self.height // 2

        a, b = np.ogrid[-y:y, -x:x]

        circle = a**2 + b**2

        if inverse:
            return np.logical_and(diam2**2 > circle, circle > diam1**2)
        else:
            return np.logical_or(diam1**2> circle,  diam2**2 < circle)


class PassFilterDialog(Dialog, QDialog, ff.Ui_Dialog):
    mask_accepted = Signal(np.ndarray)
    updated = Signal(np.ndarray)
    mask = None

    def __init__(self, low=True, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.low = low
        self.horizontalSlider.valueChanged.connect(self.update_mask)
        self.buttonBox.rejected.connect(self._clear)
        self.buttonBox.accepted.connect(self._apply_mask)

    def update_mask(self, diam):
        diam = diam if not self.low else 99 - diam
        print(diam)
        max_dim = max(self.height, self.width)
        diam = max_dim * (diam/100)
        self.mask = round_mask(diam, self.width, self.height, low=self.low)
        self.updated.emit(self.mask.copy())


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
        self.action_band_pass.triggered.connect(self.on_action_band_pass)

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
        self.toolBar.addWidget(QLabel("Color:"))
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

        self.toolBar.addWidget(QLabel("Symmetry:"))
        x_sym = QCheckBox(self.toolBar)
        x_sym.toggled.connect(self.fourier.on_x_toggle)

        opp_sym = QCheckBox(self.toolBar)
        opp_sym.toggled.connect(self.fourier.on_opp_toggle)
        self.toolBar.addWidget(QLabel("X"))
        self.toolBar.addWidget(x_sym)

        y_sym = QCheckBox(self.toolBar)
        y_sym.toggled.connect(self.fourier.on_y_toggle)
        self.toolBar.addWidget(QLabel("Y"))
        self.toolBar.addWidget(y_sym)
        self.toolBar.addWidget(QLabel("Center"))
        self.toolBar.addWidget(opp_sym)

    def update_fourier(self, image_array, cause):
        flush = False
        if cause == 'fourier':
            return
        if cause == 'load':
            flush = True

        self.fourier.update_fourier(image_array, flush=flush)

    def pass_dialog(self, dialog_type, *args, **kwargs):
        dialog = dialog_type(*args, **kwargs)
        dialog.setFourierSize(self.fourier.sizeHint())
        dialog.updated.connect(self.fourier.overlay.set)
        dialog.mask_accepted.connect(self.fourier.draw_mask_on_fourier)
        return dialog

    def on_action_band_pass(self):
        # I'm not sure if i have to keep reference to them here,
        # But I do, just in case if they'll get randomly collected. yolo
        self.bp_dialog = self.pass_dialog(BandpassDialog)
        self.bp_dialog.show()

    def on_action_low_pass(self):
        self.lp_dialog = self.pass_dialog(PassFilterDialog)
        self.lp_dialog.show()

    def on_action_high_pass(self):
        self.hp_dialog = self.pass_dialog(PassFilterDialog, low=False)
        self.hp_dialog.show()

    def on_action_resize(self):
        self.r_dialog = ResizeDialog()
        self.r_dialog.resized.connect(self.fourier.on_resize)
        self.r_dialog.show()
