import os
from collections import OrderedDict, namedtuple

from PySide import QtGui, QtCore
from PySide.QtCore import Qt
from PySide.QtGui import (QMainWindow, QFileDialog, QMdiSubWindow,
                          QImage, QLabel, QPixmap, QToolButton,
                          QSpacerItem, QWidget, QSizePolicy)

from ui.ui_main_window import Ui_MainWindow
from ui.widgets import ImageWidget, FourierWidget, HistogramWidget
from ui.widgets.fourier import Fourier
from ui.widgets.about_widget import AboutWidget

ImageWindows = namedtuple('ImageWindows', ['image', 'fourier', 'histogram'])


def current_window(get_parent_image=True):
    """ funky decorator to pass current window/parent
        of the current window as a first argument """

    def deco(func):

        def inner(self, *args, **kwargs):
            window = self.mdiArea.activeSubWindow()
            if get_parent_image:
                window = getattr(window, "mdi_parent", window)

            return func(self, window, *args, **kwargs)

        return inner

    return deco


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        #self.ui = Ui_MainWindow()
        #self.ui.setupUi(self)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolBar.addWidget(spacer)
        self.toolBar.addAction(self.action_show_info)
        self.setup_actions()

        self.action_open_file.triggered.connect(self.on_open_file)

    def setup_actions(self):
        self.action_show_fourier.toggled.connect(self.action_toggle_fourier)
        self.action_show_histogram.toggled.connect(self.action_toggle_histogram)
        self.action_show_info.triggered.connect(self.on_show_info)

    def on_open_file(self):
        file_path, _= QFileDialog.getOpenFileName(self,
                     "Open file", ".",
                     "Image Files (*.png *.jpg *.bmp *.gif *.tiff *.tif *.jpeg)")
        self.open_file(file_path)

    def maybe_save(self):
        pass

    def on_save_file(self):
        pass

    def open_file(self, file_path):
        if not file_path or not os.path.isfile(file_path):
            return

        title = os.path.basename(file_path)
        image = ImageWidget()
        fourier = FourierWidget(title)
        histogram = HistogramWidget(title)

        image.image_updated.connect(fourier.update_fourier)
        image.image_updated.connect(histogram.update_histogram)
        fourier.fourier_updated.connect(image.from_fourier)
        image.load_file(file_path)

        flags= Qt.CustomizeWindowHint |Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint
        mdi_image = self.mdiArea.addSubWindow(image)
        mdi_histogram = self.mdiArea.addSubWindow(histogram, flags)
        mdi_fourier = self.mdiArea.addSubWindow(fourier, flags)

        def close(event):
            self.action_show_fourier.setChecked(False)
            self.action_show_histogram.setChecked(False)
            mdi_fourier.close()
            mdi_histogram.close()

        image.closeEvent = close

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
        if not window:
            self.action_show_histogram.setChecked(False)
            return
        window.mdi_histogram.setVisible(state)

    @current_window()
    def action_toggle_fourier(self, window, state):
        if not window:
            self.action_show_fourier.setChecked(False)
            return
        window.mdi_fourier.setVisible(state)
        fourier_widget = window.mdi_fourier.widget()
        fourier_widget.fourier.regen_image()
        window.mdi_fourier.resize(window.mdi_fourier.sizeHint())

    def on_mdiArea_subWindowActivated(self, window):
        if not window:  # Apparently i can't select no window as a normal
            return      # usecase, but it still triggers from time to time :3

        window = getattr(window, "mdi_parent", window)
        fourier_visible = window.mdi_fourier.isVisible()
        histogram_visible = window.mdi_histogram.isVisible()

        self.action_show_fourier.setChecked(fourier_visible)
        self.action_show_histogram.setChecked(histogram_visible)

    def on_show_info(self):
        self.info_window = AboutWidget()
        self.info_window.show()
