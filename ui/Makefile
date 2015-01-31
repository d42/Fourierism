ui:
	pyside-uic main_window.ui > ui_main_window.py
	sed -i s/'QtGui.QMenuBar(MainWindow)'/'MainWindow.menuBar()'/ ui_main_window.py # Because pyside + appmenu-qt == wut

	pyside-uic image_window.ui > ui_image_window.py
	pyside-uic fourier_window.ui > ui_fourier_window.py
	pyside-uic histogram_window.ui > ui_histogram_window.py
	pyside-uic fourier_filter.ui > ui_fourier_filter.py
	pyside-uic fourier_resize.ui > ui_fourier_resize.py
	pyside-uic noise_dialog.ui > ui_noise_dialog.py
	pyside-uic noise_dialog_custom.ui > ui_noise_dialog_custom.py
	pyside-uic noise_dialog_stripes.ui > ui_noise_dialog_stripes.py
	pyside-uic noise_dialog_squares.ui > ui_noise_dialog_squares.py
	pyside-uic save_dialog.ui > ui_save_dialog.py
