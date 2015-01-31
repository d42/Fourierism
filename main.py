from PySide.QtGui import QApplication
import sys
from ui.widgets import MainWindow


def main():
    app = QApplication(sys.argv)

    path = sys.argv[1] if len(sys.argv) > 1 else None
    main = MainWindow()
    main.showMaximized()
    if path:
        main.open_file(path)

    app.exec_()

if __name__ == '__main__':
    main()
