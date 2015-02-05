import sys
from io import StringIO

import matplotlib
matplotlib.use("QT4Agg")
from PySide.QtGui import QApplication

from ui.widgets import MainWindow


def main():

    # Ugly hack, because it goes insane without running terminal(wtf)
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    app = QApplication(sys.argv)

    path = sys.argv[1] if len(sys.argv) > 1 else None
    main = MainWindow()
    main.showMaximized()
    if path:
        main.open_file(path)

    app.exec_()

if __name__ == '__main__':
    main()
