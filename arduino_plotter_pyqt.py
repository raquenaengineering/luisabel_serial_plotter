# standard imports #
import sys											# deal with OS, open files and so
import time 										# delays, and time measurement ?


# qt imports #
from PyQt5.QtWidgets import (
	QApplication,
	QMainWindow,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QComboBox,
	QLineEdit,
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


# GLOBAL VARIABLES #

COLORS = [
# 17 undertones https://lospec.com/palette-list/17undertones
"#000000",
"#141923",
"#414168",
"#3a7fa7",
"#35e3e3",
"#8fd970",
"#5ebb49",
"#458352",
"#dcd37b",
"#fffee5",
"#ffd035",
"#cc9245",
"#a15c3e",
"#a42f3b",
"#f45b7a",
"#c24998",
"#81588d",
"#bcb0c2",
"#ffffff",
]

# ~ SERIAL_SPEEDS = [
# ~ 300,
# ~ 1200,
# ~ 2400,
# ~ 4800,
# ~ 9600,
# ~ 19200,
# ~ 38400,
# ~ 57600,
# ~ 74880,
# ~ 115200,
# ~ 230400,
# ~ 250000,
# ~ 500000,
# ~ 1000000,
# ~ 2000000

# ~ ]

SERIAL_SPEEDS = [
"300",
"1200",
"2400",
"4800",
"9600",
"19200",
"38400",
"57600",
"74880",
"115200",
"230400",
"250000",
"500000",
"1000000",
"2000000"
]

ENDLINE_OPTIONS = [
"No Line Adjust",
"New Line",
"Carriage Return",
"Both NL & CR"
]




# MAIN WINDOW #


class MyGraph(pg.PlotWidget):
	def __init__(self):
		super().__init__()			
		self.setBackground([200,200,200])								# changing default background color.
		# do something to set the default axes range

class MainWindow(QMainWindow): 
	def __init__(self):
		super().__init__()
		# window stuff #
		self.setWindowTitle("Arduino Plotter PyQt")						# relevant title 
		self.setWindowIcon(QIcon("RE_logo_32p.png"))					# basic raquena engineering branding
		self.resize(1200,800)											# setting initial window size
		# central widget #
		self.widget = QWidget()
		self.layoutV1 = QVBoxLayout()									# that's how we will lay out the window
		self.widget.setLayout(self.layoutV1)
		self.setCentralWidget(self.widget)							
		# graph / plot #
		self.plot_frame = MyGraph()										# we'll use a custom class, so we can modify the defaults via class definition
		self.layoutV1.addWidget(self.plot_frame)
		# buttons / menus # 
		self.layoutH1 = QHBoxLayout()
		self.layoutV1.addLayout(self.layoutH1)
		self.combo_serial_speed = QComboBox()
		self.combo_serial_speed.setEditable(False)						# by default it isn't editable, but just in case.
		self.combo_serial_speed.addItems(SERIAL_SPEEDS)
		self.layoutH1.addWidget(self.combo_serial_speed)				# 
		self.label_baud = QLabel("baud")
		self.layoutH1.addWidget(self.label_baud)
		self.textbox_send_command = QLineEdit()
		self.layoutH1.addWidget(self.textbox_send_command)
		self.b_send = QPushButton("Send")
		self.layoutH1.addWidget(self.b_send)
		self.combo_endline_params = QComboBox()
		self.combo_endline_params.addItems(ENDLINE_OPTIONS)
		self.layoutH1.addWidget(self.combo_endline_params)


		
		# show and done #
		self.show()



	# ~ # creates a full palete with as many buttons as colors as defined in COLORS
	# ~ def add_palette_buttons(self,layout):
		# ~ for c in COLORS:
			# ~ b = QPaletteButton(c)
			# ~ b.pressed.connect(lambda c = c: self.canvas.set_pen_color(c))	# not completely sure about how lambda functions work
			# ~ layout.addWidget(b)
			
		
		
		

		# ~ self.counter = 0
		# ~ self.l = QLabel("Start")
		# ~ b = QPushButton("DANGER!")
		# ~ b.pressed.connect(self.oh_no)
		# ~ self.layout.addWidget(self.l)
		# ~ self.layout.addWidget(b)

		


app = QApplication(sys.argv)
mw = MainWindow()
app.exec_()
