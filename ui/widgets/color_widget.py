from PySide import QtGui, QtCore

from PySide.QtGui import (QMainWindow, QFileDialog, QMdiSubWindow, QPainter,
                          QLabel, QPixmap, QToolButton, QWidget, QColor,
                          QFrame)


class ColorWidget(QFrame):

    def __init__(self, parent=None):
        self.color = QColor(255, 255, 255)
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel|QFrame.Raised)

    def paintEvent(self, event):
        super().paintEvent(event)

        #painter = QPainter(self)
        #painter.fillRect(event.rect(), self.color)

    def sizeHint(self):
        return QtCore.QSize(24, 20)
