# standard imports #
import sys											# deal with OS, open files and so
import time 										# delays, and time measurement ?


# qt imports #
from PyQt5.QtWidgets import (
	QApplication,
	QMainWindow,
	QVBoxLayout,
	QLabel,
	QPushButton,

	QSystemTrayIcon,
	QTextEdit,
	QMenu,
	QAction,
	QWidget
)

from PyQt5.QtGui import (
	QIcon
)

from PyQt5.QtCore import(
	Qt
)

import pyqtgraph as pg


# MAIN WINDOW #


class MyGraph(pg.PlotWidget):
	def __init__(self):
		super().__init__()			
		self.setBackground([255,255,255])								# changing default background color.

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		
		self.setWindowTitle("Arduino Plotter PyQt")						# relevant title 
		self.setWindowIcon(QIcon("RE_logo_32p.png"))					# basic raquena engineering branding
		self.resize(1200,800)											# setting initial window size
		
		#self.plot_frame = pg.PlotWidget(self)
		self.plot_frame = MyGraph()										# we'll use a custom class, so we can modify the defaults via class definition
		
		self.setCentralWidget(self.plot_frame)

		self.counter = 0
		layout = QVBoxLayout()
		self.l = QLabel("Start")
		b = QPushButton("DANGER!")
		b.pressed.connect(self.oh_no)
		layout.addWidget(self.l)
		layout.addWidget(b)
		w = QWidget()
		w.setLayout(layout)
		
		self.show()

	def oh_no():
		pass



app = QApplication(sys.argv)
mw = MainWindow()
app.exec_()
