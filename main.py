from PySide import QtGui, QtCore
import sys
from ui.widgets import MainWindow



def main():
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    app.exec_()

if __name__ == '__main__':
    main()
