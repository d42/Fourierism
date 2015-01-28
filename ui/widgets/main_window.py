import os
from collections import OrderedDict, namedtuple

from PySide import QtGui, QtCore
from PySide.QtGui import (QMainWindow, QFileDialog, QMdiSubWindow,
                          QImage, QLabel, QPixmap, QToolButton)

from ui.ui_main_window import Ui_MainWindow
from ui.widgets import ImageWidget, FourierWidget, HistogramWidget
from ui.widgets.fourier import Fourier


ImageWindows = namedtuple('ImageWindows', ['image', 'fourier', 'histogram'])


def current_window(get_parent_image=True):

    def deco(func):

        def inner(self, *args, **kwargs):
            window = self.ui.mdiArea.activeSubWindow()
            if get_parent_image:
                window = getattr(window, "mdi_parent", window)

            return func(self, window, *args, **kwargs)

        return inner

    return deco


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_actions()

        self.ui.action_open_file.triggered.connect(self.on_open_file)

    def setup_actions(self):
        ui = self.ui
        ui.action_show_fourier.toggled.connect(self.action_toggle_fourier)
        ui.action_show_histogram.toggled.connect(self.action_toggle_histogram)

    def on_open_file(self):
        file_path, filter = QFileDialog.getOpenFileName()
        self.open_file(file_path)

    def open_file(self, file_path):
        title = os.path.basename(file_path)
        image = ImageWidget()
        fourier = FourierWidget(title)
        histogram = HistogramWidget(title)

        image.image_updated.connect(fourier.update_fourier)
        image.image_updated.connect(histogram.update_histogram)
        fourier.fourier_updated.connect(image.from_fourier)
        image.load_file(file_path)

        mdi_image = self.ui.mdiArea.addSubWindow(image)
        mdi_histogram = self.ui.mdiArea.addSubWindow(histogram)
        mdi_fourier = self.ui.mdiArea.addSubWindow(fourier)

        mdi_image.mdi_fourier = mdi_fourier
        mdi_image.mdi_histogram = mdi_histogram

        mdi_fourier.mdi_parent = mdi_image
        mdi_histogram.mdi_parent = mdi_image

        mdi_image.show()

    def on_operation(self, active_window, image_function):
        """:type active_window: MdiImage"""
        active_window.update(image_function)
        self.cache.flush(active_window)
        self.update_widgets(active_window.image_array)

    @current_window()
    def action_toggle_histogram(self, window, state):
        window.mdi_histogram.setVisible(state)

    @current_window()
    def action_toggle_fourier(self, window, state):
        window.mdi_fourier.setVisible(state)
        window.mdi_fourier.resize(window.mdi_fourier.sizeHint())

    def on_fourier_update(self, ftt_array):
        print("PENIS PENIS PENIS")

    def on_subwindow_change(self, window):
        if not window:  # Apparently i can't select no window as a normal
            return      # usecase, but it still triggers from time to time :3

        window = getattr(window, "mdi_parent", window)
        fourier_visible = window.mdi_fourier.isVisible()
        histogram_visible = window.mdi_histogram.isVisible()

        self.ui.action_show_fourier.setChecked(fourier_visible)
        self.ui.action_show_histogram.setChecked(histogram_visible)
