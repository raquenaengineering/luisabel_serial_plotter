# standard imports #
import sys											# deal with OS, open files and so
import time 										# delays, and time measurement ?

import serial										# required to handle serial communication
import serial.tools.list_ports						# to list already existing ports

import logging
#logging.basicConfig(level=logging.DEBUG)		# enable debug messages


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
	QMenuBar,
	QToolBar,
	QStatusBar,

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
	Qt,
	QSize
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
		self.showGrid(x = True, y = True, alpha = 0.5)
		# do something to set the default axes range
		self.setRange(xRange = [0,1000], yRange = [-200,200])
		self.setLimits(xMin=0, xMax=1000000, yMin=-1000, yMax=1000)		# THIS MAY ENTER IN CONFIG WITH PLOTTING !!!
	
		
class QPaletteButton(QPushButton):
	def __init__(self,color):							# color as input parameter
		super().__init__()
		self.setFixedSize(QSize(24,24))
		self.color = color
		self.setStyleSheet("background-color: " + color)				# the book uses c-ish like syntax. 
					

class MainWindow(QMainWindow): 
	
	# class variables #
	serial_ports = list													# list of serial ports detected, probably this is better somewhere else !!!
	
	# constructor # 
	def __init__(self):
		super().__init__()
		# window stuff #
		self.setWindowTitle("Arduino Plotter PyQt")						# relevant title 
		self.setWindowIcon(QIcon("RE_logo_32p.png"))					# basic raquena engineering branding
		self.resize(1200,800)											# setting initial window size
		# menubar #
		menu = self.menuBar()											# by default, the window already has an instance/object menubar
		# file #
		self.file_menu = menu.addMenu("&File")
		self.serial_port_menu = self.file_menu.addMenu("Serial Port")
		self.update_serial_ports()

		# about #
		help_menu = menu.addMenu("&Help")
		about_menu = help_menu.addAction("About")
		
		
		button_action = QAction()
		self.file_menu.addAction(button_action)
		
		#self.toolbar.setIconSize(Qsize(16,16))
		#self.addToolBar(self.toolbar)
		#self.menubar.addMenu("&file")
		
		
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
		self.combo_serial_speed.currentTextChanged.connect(				# on change on the serial speed textbox, we call the connected mthod
			self.change_serial_speed) 									# we'll figure out which is the serial speed at the method (would be possible to use a lambda?) 
		self.layoutH1.addWidget(self.combo_serial_speed)				# 
		self.label_baud = QLabel("baud")
		self.layoutH1.addWidget(self.label_baud)
		self.textbox_send_command = QLineEdit()
		self.textbox_send_command.returnPressed.connect(self.send_serial)			# sends command via serial port
		self.layoutH1.addWidget(self.textbox_send_command)
		self.b_send = QPushButton("Send")											
		self.b_send.clicked.connect(self.send_serial)								# same action as enter in textbox
		self.layoutH1.addWidget(self.b_send)
		self.combo_endline_params = QComboBox()
		self.combo_endline_params.addItems(ENDLINE_OPTIONS)
		self.combo_endline_params.currentTextChanged.connect(self.change_endline_style)
		self.layoutH1.addWidget(self.combo_endline_params)
		# ~ self.layoutH2 = QHBoxLayout()
		# ~ self.layoutV1.addLayout(self.layoutH2)
		# ~ self.add_palette_buttons(self.layoutH2)
		
		# status bar #
		self.status_bar = QStatusBar()
		self.setStatusBar(self.status_bar)
		self.status_bar.showMessage("Not Connected")
		# 3. write text saying no serial port is connected

		# show and done #
		self.show()
		
		
		# actions #		
		
	def send_serial(self):
		print("Send Serial")
		self.textbox_send_command.setText("")
		#2.delete textbox content. 
		#self.centralWidget().setText("BOOM!")
		
		# here the serial send command # 
	
	# other methods # 
		
	def get_serial_ports(self):
				
		logging.debug('Running get_serial_ports')
		serial_port = None
		self.serial_ports = list(serial.tools.list_ports.comports())
		for p in self.serial_ports:
			logging.debug(p)
		logging.debug("---------------------------------------------------")
		port_names = []		# we store all port names in this variable
		for port in self.serial_ports:
			port_names.append(port[0])	# here all names get stored
		logging.debug(port_names)
		logging.debug("---------------------------------------------------")
		
		# Note: not all the ports are valid options, so we could discard the that aren't interesting USING THE DESCRIPTION!
		port_descs = []
		for port in self.serial_ports:
			port_descs.append(port[1])
		logging.debug(port_descs)
		logging.debug("---------------------------------------------------")
		

		
	def change_serial_speed(self):
		print("change_serial_speed method called")
		text_val = self.combo_serial_speed.currentText()
		print(text_val)
		
	def change_endline_style(self):										# this and previous method are the same, use lambdas?
		endline_style = self.combo_endline_params.currentText()
		print(endline_style)

		
	def select_serial_port(self):
		serial_port_name = 	"s"
		print(serial_port_name)
		
		
		
	def on_port_select(self):				# callback when COM port is selected at the menu.
		#1. get the selected port name via the text. 
		#2. open a serial communication.
		pass
		
	def serial_connect(self, port_name):
		print("serial_connect method called")
		print(port_name)
		print("port name " + port_name)


	# creates a full palete with as many buttons as colors as defined in COLORS
	def add_palette_buttons(self,layout):
		for c in COLORS:
			b = QPaletteButton(c)
			b.pressed.connect(lambda c = c: self.canvas.set_pen_color(c))	# not completely sure about how lambda functions work
			layout.addWidget(b)


	def update_serial_ports(self):										# we update the list every time we go over the list of serial ports.
		# here we need to add an entry for each serial port avaiable at the computer
		# 1. How to get the list of available serial ports ?
		self.get_serial_ports()											# meeded to list the serial ports at the menu
		# 3. How to ensure which serial ports are available ? (grey out the unusable ones)
		# 4. How to display properly each available serial port at the menu ?
		print (self.serial_ports)
		if self.serial_ports != []:
			for port in self.serial_ports:
				port_name = port[0]
				print(port_name)
				b = self.serial_port_menu.addAction(port_name)
				b.triggered.connect((lambda : self.serial_connect(port_name)))				# just need to add somehow the serial port name here, and we're done.


				# here we need to add the connect method to the action click, and its result
				
		else:
				self.noserials = serial_port_menu.addAction("No serial Ports detected")
				self.noserials.setDisabled(True)
				 	
		
app = QApplication(sys.argv)
mw = MainWindow()
app.exec_()
