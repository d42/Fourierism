ui:
	pyside-uic main_window.ui > ui_main_window.py
	sed -i s/'QtGui.QMenuBar(MainWindow)'/'MainWindow.menuBar()'/ ui_main_window.py # Because pyside + appmenu-qt == wut
