from ui.ui_about_dialog import Ui_Form
from PySide.QtGui import QWidget

class AboutWidget(QWidget, Ui_Form):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
