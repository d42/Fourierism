from ui.ui_main_window import Ui_MainWindow
from PySide.QtGui import QMainWindow, QFileDialog


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


    def setup_actions(self):
        pass

    def on_open_file(self):
        file_path = QFileDialog()
        pass
