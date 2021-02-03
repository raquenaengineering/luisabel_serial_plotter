
import sys

from PyQt5.QtWidgets import (
	QApplication,
	)

from main_window import *

## MAIN ##

app = QApplication(sys.argv)
app.setStyle("Fusion")													# required to use it here
mw = MainWindow()
app.exec_()

