from PySide import QtGui
from PySide.QtGui import (QMdiSubWindow, QImage, QPixmap, QWidget, qRgb)
from PySide.QtCore import Qt, Signal, Slot
import numpy as np

from ui.ui_histogram_window import Ui_HistogramWindow




class MdiHistogram(QMdiSubWindow):

    def __init__(self, parent_image, parent=None):


