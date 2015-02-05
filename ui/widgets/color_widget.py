from PySide.QtGui import QPainter, QColor, QFrame, QWidgetAction, QDial, QMenu
from PySide.QtCore import Qt, Signal, QSize


class QColorDial(QDial):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setNotchesVisible(False)
        self.setMaximum(255)
        self.setMinimum(0)



class ColorWidget(QFrame):
    color_changed = Signal(int)

    def __init__(self, parent=None):
        self.color = QColor(0, 0, 0)
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel|QFrame.Raised)

        dial = QColorDial(self)
        dial.sliderMoved.connect(self.set_color)

        action = QWidgetAction(self)
        action.setDefaultWidget(dial)
        self.menu = QMenu()
        self.menu.addAction(action)

        #self.addAction(action)
        #self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.fillRect(event.rect(), self.color)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.menu.exec_(self.mapToGlobal(event.pos()))

    def sizeHint(self):
        return QSize(24, 20)

    def set_color(self, color):
        self.color = QColor(color, color, color)
        self.color_changed.emit(color)
        self.update()

