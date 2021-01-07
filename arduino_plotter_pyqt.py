# standard imports #
import sys											# deal with OS, open files and so
import time 										# delays, and time measurement ?
import random										# random numbers

import serial										# required to handle serial communication
import serial.tools.list_ports						# to list already existing ports


import numpy as np 									# required to handle multidimensional arrays/matrices

import logging
#logging.basicConfig(level=logging.DEBUG)			# enable debug messages
logging.basicConfig(level = logging.WARNING)

# custom packages #

import pyqt_custom_palettes							# move at some point to a repo, and add it as a submodule dark_palette, and more.


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
	QDialog,
	QMessageBox,														# Dialog with extended functionality. 
	QShortcut,


	QSystemTrayIcon,
	QTextEdit,
	QMenu,
	QAction,
	QWidget
)

from PyQt5.QtGui import (
	QIcon,
	QKeySequence
)

from PyQt5.QtCore import(
	Qt,
	QThreadPool,
	QRunnable,
	QObject,
	QSize,
	pyqtSignal,															# those two are pyqt specific. 
	pyqtSlot,
	QTimer																# nasty stuff

)

import pyqtgraph as pg


# GLOBAL VARIABLES #

SERIAL_BUFFER_SIZE = 1000												# buffer size to store the incoming data from serial, to afterwards process it.
SEPARATOR = "----------------------------------------------------------"


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


# THREAD STUFF #

class Worker_serialport(QRunnable):
	
	
	# class variables #
	
	done = False														# if done, thread should finish.
	timeouts = 0														# counts number of timeouts the serial port has made until the moment.

	# ~ ## constructor ##													# how does it work with the constructor and the run method ??
	# ~ def __init__(self):														
		# ~ self.signals = WorkerSignals_serialport()						# signals triggered by the thread, to communicate with the MAIN WINDOW
		
		
	## run method ##
	def run(self):
		print("Thread Start")
		
		#1 . CREATE A SERIAL PORT OBJECT.
		
		self.serial_port = serial.Serial()
		
		
		#2 . GET THE REQUIRED CONFIGURATION DATA OF THER SERIAL PORT FROM MAIN WINDOW
		#3 . LOOP GETTING THE DATA WHILE THE PORT IS OPEN.
		
		self.serial_connect(mw.serial_port_name)									# using a global variable for this is a bad idea!!! --> dunno how to do it better ...
		
		while ((self.serial_port.is_open == True) and (self.done == False)):		# move the isopen port to the place WHERE THE DONE FLAG IS ENABLED.						
			
			# 1. get everything to a string for easy handling
			
			readed = self.serial_port.read_until(mw.endline)						# this should block the loop, so needs to go to a THREAD
			logging.debug("String as readed: ")
			logging.debug(readed)	# THIS IS BYTES! SHOULD BE CONVERTED!!!		
			logging.debug("Endline: ")
			logging.debug(mw.endline)
			logging.debug("Readed.endline found at character: ")
			i = readed.find(mw.endline)									# index where the the endline starts.
			readed = readed[:i]											# this removes the endline.								
			readed = readed.decode("utf-8")								# convert to string
			logging.debug("Readed:")
			logging.debug(readed)
			
			# 2. perform data processing as required (START WITH ARDUINO STYLE, AND ADD OTHER STYLES).
		
			vals = readed.replace(' ',',')								# replace empty spaces for commas. 
			vals = vals.split(',')										# arduino serial plotter splits with both characters.
			
			logging.debug("Vals: ")
			logging.debug(vals)
			valsf = []

			if(vals[0] == ''):
				print("Timeout")
			else:	
				try:
					for val in vals:
						valsf.append(float(val))
					# ~ print("valsf")
					# ~ print(valsf)
				except:
					logging.debug("It contains also text");
					# add to a captions vector
					text_vals = vals
				
			
			if(mw.plot_frame.dataset == []):							# if the dataset is empty (a dataset reset function may  be useful)
				for val in valsf:
					mw.plot_frame.dataset.append([])
			else:														# if already data, we append to each sub array. 
				for i in range(0,len(valsf)):							# this may not be the greatest option.
					mw.plot_frame.dataset[i].append(valsf[i])
				mw.plot_frame.dataset_changed = True					# we've changed the dataset, so we update the plot.
			
			# 4. MANAGE MESSAGES TO BE SENT VIA SERIAL.
			if(mw.serial_message_to_send != None):
				logging.debug("New message to be sent:")
				logging.debug(mw.serial_message_to_send)
				# 4.1 convert the message to bytes (default is encoded)
				message = bytes(mw.serial_message_to_send,"utf-8")
				self.serial_port.write(message,)						# send message
				mw.serial_message_to_send = None						# reset message
				logging.debug("message sent")

		# 5. CLOSE THE OPEN PORT. 	
		
		logging.debug("serial_port.is_open:")
		logging.debug(self.serial_port.is_open)
		logging.debug("done")
		logging.debug(self.done)		
			
		mw.on_button_disconnect_click()									# used to reenable the serial Connect button, just in case there's a crash
		logging.debug("Thread Complete")
		logging.debug(SEPARATOR)
		
	def serial_connect(self, port_name):
		logging.debug("serial_connect method called")
		logging.debug(port_name)
		logging.debug("port name " + port_name)

		try:															# closing port just in case was already open. (SHOULDN'T BE !!!)
			self.serial_port.close()
			logging.debug("Serial port closed")	
			logging.debug("IT SHOULD HAVE BEEN ALWAYS CLOSED, REVIEW CODE!!!")	# even though the port can't be closed, this message is shown. why ???
		except:
			logging.debug("serial port couldn't be closed")
			logging.debug("Wasn't open, as it should always be")


		try:															# try to establish serial connection 
			self.serial_port = serial.Serial(		# serial constructor
				port=port_name, 
				baudrate= mw.serial_baudrate,		
				#baudrate = 115200,
				#bytesize=EIGHTBITS, 
				#parity=PARITY_NONE, 
				#stopbits=STOPBITS_ONE, 
				#timeout=None, 
				timeout=3,										# we'll need a timeout just in case there's no communication
				xonxoff=False, 
				rtscts=False, 
				write_timeout=None, 
				dsrdtr=False, 
				inter_byte_timeout=None, 
				exclusive=None
				)
			
		except Exception as e:								# both port open, and somebody else blocking the port are IO errors.
			logging.debug("ERROR OPENING SERIAL PORT")
			desc = str(e)
			logging.debug(type(e))
			logging.debug(desc)
			i = desc.find("Port is already open.")
			if(i != -1):
				print("PORT ALREADY OPEN BY THIS APPLICATION")
			logging.debug(i)
			
			i = desc.find("FileNotFoundError")
			if(i != -1):
				logging.debug("DEVICE IS NOT CONNECTED, EVEN THOUGH PORT IS LISTED")
				mw.on_port_error(2)										# 
					
			i = desc.find("PermissionError")
			if(i != -1):
				logging.debug("SOMEONE ELSE HAS OPEN THE PORT")
				mw.on_port_error(3)										# shows dialog the por is used (better mw or thread?) --> MW, IT'S GUI.
			
			i = desc.find("OSError")
			if(i != -1):
				logging.debug("BLUETOOTH DEVICE NOT REACHABLE ?")	
				mw.on_port_error(4)
				
				
					
		except:
			logging.debug("UNKNOWN ERROR OPENING SERIAL PORT")

		else:															# IN CASE THERE'S NO EXCEPTION (I HOPE)
			logging.debug("SERIAL CONNECTION SUCCESFUL !")
			# here we should also add going  to the "DISCONNECT" state.
			
		logging.debug("serial_port.is_open:")
		logging.debug(self.serial_port.is_open)
		logging.debug("done: ")
		logging.debug(self.done)			

class WorkerSignals_serialport(QObject):
	port_error_other = pyqtSignal(str)
	

class MyGraph(pg.PlotWidget):
	
	
	max_points = 1000													# maximum points per plot
	max_plots = 16														# maximum number of plots
	first = True														# first iteration only creating the plots
	
	dataset = []							
	plot_refs = []
													
	dataset_changed = False

	#dataset = np.array()
	
	def __init__(self):
		super().__init__()		
		pg.setConfigOptions(antialias=True)							# antialiasing for nicer view. 
		#self.setBackground([200,200,200])								# changing default background color.
		self.setBackground([70,70,70])									# changing default background color.
		self.showGrid(x = True, y = True, alpha = 0.5)
		# do something to set the default axes range
		#self.setRange(xRange = [0,1000], yRange = [-200,200])
		self.setRange(xRange = [0,50], yRange = [0,256])
		self.setLimits(xMin=-10, xMax=1000000, yMin=-1000, yMax=1000)		# THIS MAY ENTER IN CONFIG WITH PLOTTING !!!
		self.enableAutoRange(axis='x', enable=True)						# enabling autorange for x axis
		legend = self.addLegend()
		
		self.plot_timer = QTimer()										# used to update the 
		self.plot_timer.timeout.connect(self.on_plot_timer)				# regularly check if the serial error flag is set
		self.plot_timer.start(10)										# will also control the refresh rate.	
		
		
		# ~ c1 = self.plot([1,3,2,4], pen='y', name='Yellow Plot')
		# ~ c2 = self.plot([2,1,4,3], pen='b', fillLevel=0, fillBrush=(255,255,255,30), name='Blue Plot')
		# ~ c3 = self.addLine(y=4, pen='y')
		
		#style1 = pg.PlotDataItem(pen=None,symbol='o',symbolBrush=["m"])
		# ~ legend.addItem(name = "Variable 1", item = 1)


	def add_plots(self):												# optionally, make possible single or multiple plots
		# FIRST: CREATE THE PLOTS 
			# bring this to the graph creator 
		print("Add graph.plots_method called")
			
		#for dataplot in self.dataset:
		for i in range (len(self.dataset)):
			print("val of i:" + str(i))
			# HOW TO REFERENCE THE PLOTS CREATED ON THIS WAY ??? #
			# plot = self.plot(self.dataset[i], pen = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)), name ="Plot" + str(i))
			# p = self.plot(self.dataset[i], pen = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)),name ="Plot" + str(i))
			p = self.plot(self.dataset[i], pen = (COLORS[i]),name ="Plot" + str(i))

			self.plot_refs.append(p)

	def on_plot_timer(self):

		# MOVE TO NUMPY N-DIMENSIONAL ARRAYS #

		# update all plots
		#c1 = self.plot([1,3,2,4,5,12,3,1,5,6,9,7,8], pen='y')	
			
		# SECOND: UPDATE THE PLOTS:
			
		if(self.dataset_changed == True):											# redraw only if there are changes on the dataset
			if self.first == True:
				self.add_plots()
				self.first = False
			self.dataset_changed = False
			for i in range(len(self.dataset)):
				self.plot_refs[i].setData(self.dataset[i]) 
			# ~ for dataplot in self.dataset:
				# ~ #self.plot(dataplot, pen = 'r')
				# ~ #self.plot(dataplot, pen = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)), name = "17")
				# ~ self.setData
			
		
# MAIN WINDOW #			

class MainWindow(QMainWindow): 
	
	# class variables #
	serial_ports = list													# list of serial ports detected, probably this is better somewhere else !!!
	serial_port = None													# maybe better to decleare it somewhere else ??? serial port used for the comm.
	serial_port_name = None												# used to pass it to the worker dealing with the serial port.
	serial_baudrate = 115200											# default baudrate, ALL THOSE VARIABLES SHOULD CONNECT TO WORKER_SERIALPORT!
	endline = b'\r\n'													# default value for endline is NL 
	error_type = None													# used to try to fix the problem with dialog window, delete if can't fix !!!
	serial_message_to_send = None										# if not none, is a message to be sent via serial port (the worker sends)
	full_screen_flag = False
	
	
	# constructor # 
	def __init__(self):
		
		super().__init__()
		
		# thread stuff # 
		self.threadpool = QThreadPool()
		# serial port worker created now on button press							
		print(
			"Multithreading, max. Number of Threads:  " +
			str(self.threadpool.maxThreadCount())
		)
		
		# timers #																			# AT LEAST ONE TO UPDATE THE PLOT !!!
		self.internal_tasks_timer = QTimer()												# used for nasty stuff
		self.internal_tasks_timer.timeout.connect(self.handle_port_errors)					# regularly check if the serial error flag is set
		self.internal_tasks_timer.start(100)

		# shortcuts #
		
		# f keys shortcuts #
		self.sc_f11 = QShortcut(QKeySequence("F11"), self)									# F11
		self.sc_f11.activated.connect(self.full_screen)
		self.sc_f10 = QShortcut(QKeySequence("F10"), self)									# F10
		self.sc_f10.activated.connect(self.on_sc_f10)
		# Other shortcuts #
		self.sc_f = QShortcut(QKeySequence('f'), self)										# f
		self.sc_f.activated.connect(self.full_screen)
		# ~ self.sc_c = QShortcut(QKeySequence('c'), self)										# c		// c should disable itself, until d pressed.
		# ~ self.sc_c.activated.connect(self.on_button_connect_click)
		# ~ self.sc_d = QShortcut(QKeySequence('d'), self)										# d
		# ~ self.sc_d.activated.connect(self.on_button_disconnect_click)	
		self.sc_u = QShortcut(QKeySequence('u'), self)										# u
		self.sc_u.activated.connect(self.update_serial_ports)	
		self.palette = pyqt_custom_palettes.dark_palette()
		
		# theme(palette) #
		self.setPalette(self.palette)
		
		# window stuff #
		self.setWindowTitle("Arduino Plotter PyQt")						# relevant title 
		self.setWindowIcon(QIcon("RE_logo_32p.png"))					# basic raquena engineering branding
		self.resize(1200,800)											# setting initial window size
		# menubar #
		menu = self.menuBar()											# by default, the window already has an instance/object menubar
		# file #
		self.file_menu = menu.addMenu("&File")
		self.serial_port_menu = self.file_menu.addMenu("Serial Port")
		#self.serial_port_menu.triggered.connect(self.update_serial_ports)	# updates the serial port list everytime we click on it.
		#self.update_serial_ports()										# needs to be moved after the declaration of update_serial_ports!!!	
		self.refresh_menu = self.file_menu.addAction("Refresh")
		self.refresh_menu.triggered.connect(self.update_serial_ports)

		# Preferences #
		self.preferences_menu = menu.addMenu("&Preferences")
		# theme #
		self.theme_submenu = self.preferences_menu.addMenu("Theme")
		self.dark_theme_option = self.theme_submenu.addAction("Dark")
		self.dark_theme_option.triggered.connect(self.set_dark_theme)
		self.light_theme_option = self.theme_submenu.addAction("Light")
		self.light_theme_option.triggered.connect(self.set_light_theme)
		self.re_theme_option = self.theme_submenu.addAction("Raquena")
		self.re_theme_option.triggered.connect(self.set_re_theme)




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
		# connect button #
		self.button_serial_connect = QPushButton("Connect")
		self.button_serial_connect.clicked.connect(self.on_button_connect_click)
		self.layoutH1.addWidget(self.button_serial_connect)
		# disconnect button #
		self.button_serial_disconnect = QPushButton("Disconnect")
		self.button_serial_disconnect.clicked.connect(self.on_button_disconnect_click)
		self.button_serial_disconnect.setEnabled(False)
		self.layoutH1.addWidget(self.button_serial_disconnect)
		# combo serial port #
		self.combo_serial_port = QComboBox()
		self.layoutH1.addWidget(self.combo_serial_port)
		self.update_serial_ports()
		self.combo_serial_port.currentTextChanged.connect(				# changing something at this label, triggers on_port select, which should trigger a serial port characteristics update.
			self.on_port_select)
		self.label_port = QLabel("Port")
		self.layoutH1.addWidget(self.label_port)
		# combo serial speed #
		self.combo_serial_speed = QComboBox()
		self.combo_serial_speed.setEditable(False)						# by default it isn't editable, but just in case.
		self.combo_serial_speed.addItems(SERIAL_SPEEDS)
		self.combo_serial_speed.setCurrentIndex(9)						# this index corresponds to 115200 as default baudrate.
		self.combo_serial_speed.currentTextChanged.connect(				# on change on the serial speed textbox, we call the connected mthod
			self.change_serial_speed) 									# we'll figure out which is the serial speed at the method (would be possible to use a lambda?) 
		self.layoutH1.addWidget(self.combo_serial_speed)				# 
		self.label_baud = QLabel("baud")
		self.layoutH1.addWidget(self.label_baud)
		# text box command #
		self.textbox_send_command = QLineEdit()
		self.textbox_send_command.returnPressed.connect(self.send_serial)			# sends command via serial port
		self.textbox_send_command.setEnabled(False)									# not enabled until serial port is connected. 
		self.layoutH1.addWidget(self.textbox_send_command)
		# send button # 
		self.b_send = QPushButton("Send")											
		self.b_send.clicked.connect(self.send_serial)								# same action as enter in textbox
		self.layoutH1.addWidget(self.b_send)
		# combo endline #
		self.combo_endline_params = QComboBox()
		self.combo_endline_params.addItems(ENDLINE_OPTIONS)
		self.combo_endline_params.setCurrentIndex(3)					# defaults to endline with CR & NL
		self.combo_endline_params.currentTextChanged.connect(self.change_endline_style)
		self.layoutH1.addWidget(self.combo_endline_params)
		
		# status bar #
		self.status_bar = QStatusBar()
		self.setStatusBar(self.status_bar)
		self.status_bar.showMessage("Not Connected")
		# 3. write text saying no serial port is connected
		
		# show and done #		
		self.show()
		
		# other stuff which can't be done before #
		self.serial_port_name = self.combo_serial_port.currentText()	
		# self.serial_baudrate = ...
		# self.endline = ...
		

	# on close #
		
	def closeEvent(self, event):

		print("CLOSING AND CLEANING UP:")
		super().close()
		
		
		#event.ignore()													# extremely useful to ignore the close event !
	
	# actions #		
		
	def send_serial(self):												# do I need another thread for this ???
		logging.debug("Send Serial")
		command = self.textbox_send_command.text()						# get what's on the textbox. 
		self.textbox_send_command.setText("")		
		# here the serial send command # 
		self.serial_message_to_send = command							# this should have effect on the serial_thread
		logging.debug("serial_message_to_send")
		logging.debug(self.serial_message_to_send)
	
	# other methods # 
		
	def get_serial_ports(self):			# REWRITE THIS FUNCTION TO USE A DICTIONARY, AND MAKE IT WAY CLEANER !!!
				
		logging.debug('Running get_serial_ports')
		serial_port = None
		self.serial_ports = list(serial.tools.list_ports.comports())	# THIS IS THE ONLY PLACE WHERE THE OS SERIAL PORT LIST IS READ. 	
		
		port_names = []		# we store all port names in this variable
		port_descs = []		# all descriptions
		port_btenums = []	# all bluetooth enumerations, if proceeds
		for port in self.serial_ports:
			port_names.append(port[0])	# here all names get stored
			port_descs.append(port[1])
			port_btenums.append(port[2])
			
		for name in port_names:
			logging.debug(name)
		logging.debug("---------------------------------------------------")

		for desc in port_descs:
			logging.debug(desc)
		logging.debug("---------------------------------------------------")

		for btenum in port_btenums:
			logging.debug(btenum)
		logging.debug("---------------------------------------------------")
						
		# remove bad BT ports (windows creates 2 ports, only one is useful to connect)
		
		for port in self.serial_ports:
			
			port_desc = port[1]
			
			if (port_desc.find("Bluetooth") != -1):						# Bluetooth found on description,so is a BT port (good or bad, dunno yet)
				
				# Using the description as the bt serial ports to find out the "good" bluetooth port.
				port_btenum = port[2]
				port_btenum = str(port_btenum)
				splitted_enum = port_btenum.split('&')
				logging.debug(splitted_enum)							# uncomment this to see why this parameter was used to differentiate bt ports.
				last_param = splitted_enum[-1]							# this contains the last parameter of the bt info, which is different between incoming and outgoing bt serial ports. 
				last_field = last_param.split('_')						# here there is the real difference between the two created com ports
				last_field = last_field[-1]								# we get only the part after the '_'
				logging.debug(last_field)
				
				if(last_field == "C00000000"):							# this special string is what defines what are the valid COM ports.
					discarded = 0										# the non-valid COM ports have a field liked this: "00000001", and subsequent.
				else:
					discarded = 1
					logging.debug("This port should be discarded!")
					self.serial_ports.remove(port)						# removes by matching description
		
	def change_serial_speed(self):										# this function is useless ATM, as the value is asked when serial open again.
		logging.debug("change_serial_speed method called")
		text_baud = self.combo_serial_speed.currentText()
		baudrate = int(text_baud)
		#self.serial_port.baudrate.set(baudrate)	
		self.serial_baudrate = baudrate			
		logging.debug(text_baud)
		
	def change_endline_style(self):										# this and previous method are the same, use lambdas?
		logging.debug("change_endline_speed method called")
		endline_style = self.combo_endline_params.currentText()
		logging.debug(endline_style)
		# FIND A MORE ELEGANT AND PYTHONIC WAY TO DO THIS.
		if(endline_style == ENDLINE_OPTIONS[0]):						# "No Line Adjust"
			self.endline = b""
		elif (endline_style == ENDLINE_OPTIONS[1]):						# "New Line"
			self.endline = b"\n"				
		elif (endline_style == ENDLINE_OPTIONS[2]):						# "Carriage Return"
			self.endline = b"\r"		
		elif (endline_style == ENDLINE_OPTIONS[3]):						# "Both NL & CR"
			self.endline = b"\r\n"	
			
		logging.debug(self.endline)	
		
		
	def on_button_connect_click(self):									# this button changes text to disconnect when a connection is succesful.
		logging.debug("Connect Button Clicked")									# how to determine a connection was succesful ???
		self.button_serial_connect.setEnabled(False)
		self.button_serial_disconnect.setEnabled(True)
		self.combo_serial_port.setEnabled(False)
		self.combo_serial_speed.setEnabled(False)
		self.combo_endline_params.setEnabled(False)
		self.textbox_send_command.setEnabled(True)
		self.worker_serialport = Worker_serialport()					# creates a serialport worker every time we push the button, PLEASE NOTE IT ALSO NEEDS TO BE DESTROYED!!!
		self.threadpool.start(self.worker_serialport)					
		
	def on_button_disconnect_click(self):
		logging.debug("Disconnect Button Clicked")
		self.button_serial_disconnect.setEnabled(False)					# toggle the enable of the connect/disconnect buttons
		self.button_serial_connect.setEnabled(True)
		self.combo_serial_port.setEnabled(True)
		self.combo_serial_speed.setEnabled(True)
		self.combo_endline_params.setEnabled(True)
		self.textbox_send_command.setEnabled(False)
		self.worker_serialport.done = True								# finishes the thread execution
					
	def on_port_select(self,port_name):				# callback when COM port is selected at the menu.
		#1. get the selected port name via the text. 
		#2. delete the old list, and regenerate it, so when we push again the com port list is updated.
		#3. create a thread for whatever related with the serial communication, and start running it.
		#. open a serial communication. --> this belongs to the thread. 
		
		# START THE THREAD WHICH WILL BE IN CHARGE OF RECEIVING THE SERIAL DATA #
		#self.serial_connect(port_name)
		logging.debug("Method on_port_select called	")
		self.serial_port_name = port_name
		logging.debug(self.serial_port_name)
		
		
	def on_port_error(self,error_type):												# triggered by the serial thread, shows a window saying port is used by sb else.
		
		self.error_type = error_type
		
		logging.debug("Error on serial port opening detected: ")
		logging.debug(self.error_type)
		self.handle_errors_flag = True									# more global variables to fuck things up even more. 

		
	def handle_port_errors(self):										# made a trick, port_errors is a class variable (yup, dirty as fuck !!!)
		
		if(self.error_type == 1):										# this means already open, should never happen.
			logging.warning("ERROR TYPE 1")										
			d = QMessageBox.critical(
				self,
				"Serial port Blocked",
				"The serial port selected is in use by other application",
				buttons=QMessageBox.Ok
			)		
		if(self.error_type == 2):										# this means device not connected
			logging.warning("ERROR TYPE 2")
			d = QMessageBox.critical(
				self,
				"Serial Device is not connected",
				"Device not connected.\n Please check your cables/connections.  ",
				buttons=QMessageBox.Ok
			)		
		if(self.error_type == 3):										# this means locked by sb else. 
			d = QMessageBox.critical(
				self,
				"Serial port Blocked",
				"The serial port selected is in use by other application.  ",
				buttons=QMessageBox.Ok
			)

			self.on_button_disconnect_click()							# resetting to the default "waiting for connect" situation
			self.handle_errors_flag = False		
		if(self.error_type == 4):										# this means device not connected
			logging.warning("ERROR TYPE 4")
			d = QMessageBox.critical(
				self,
				"Serial Device Unreachable",
				"Serial device couldn't be reached,\n Bluetooth device too far? ",
				buttons=QMessageBox.Ok
			)		
		self.error_type = None											# cleaning unhnandled errors flags. 

	# check all themes and use lambda functions may be an option to use more themes #
	def set_dark_theme(self):
		self.palette = pyqt_custom_palettes.dark_palette()
		self.setPalette(self.palette)
		
	def set_light_theme(self):
		self.palette = pyqt_custom_palettes.light_palette()
		self.setPalette(self.palette)

	def set_re_theme(self):
		self.palette = pyqt_custom_palettes.re_palette()
		self.setPalette(self.palette)

	def update_serial_ports(self):										# we update the list every time we go over the list of serial ports.
		# here we need to add an entry for each serial port avaiable at the computer
		# 1. How to get the list of available serial ports ?
		
		self.serial_port_menu.clear()									# deletes all old actions on serial port menu	
		self.combo_serial_port.clear()
		# closing the serial port should be handled by the thread
		# this should trigger a change which will be handled by the thread.
		#self.serial_port.close()										# close the current serial port. 
		
		
		self.get_serial_ports()											# meeded to list the serial ports at the menu
		# 3. How to ensure which serial ports are available ? (grey out the unusable ones)
		# 4. How to display properly each available serial port at the menu ?
		logging.debug (self.serial_ports)
		if self.serial_ports != []:
			for port in self.serial_ports:
				port_name = port[0]
				logging.debug(port_name)
				b = self.serial_port_menu.addAction(port_name)
				# WE WON'T TRIGGER THE CONNECTION FROM THE BUTTON PUSH ANYMORE. 
				b.triggered.connect((lambda serial_connect, port_name=port_name: self.on_port_select(port_name)))				# just need to add somehow the serial port name here, and we're done.

				# here we need to add the connect method to the action click, and its result
				
			for port in self.serial_ports:								# same as adding all ports to action menu, but now using combo box. 
				port_name = port[0]	
				item = self.combo_serial_port.addItem(port_name)		# add new items 
				
				#b.currentTextChanged.connect((lambda serial_connect, port_name=port_name: self.on_port_select(port_name)))
		
		else:
				self.noserials = serial_port_menu.addAction("No serial Ports detected")
				self.noserials.setDisabled(True)

	def full_screen(self):												# it should be able to be detected from window class !!!
		if self.full_screen_flag == False:								
			self.showFullScreen()
			self.full_screen_flag = True
			logging.debug("Full Screen ENABLED")
		else:
			self.showNormal()
			self.full_screen_flag = False
			logging.debug("Full Screen DISABLED")
	
	def on_sc_f10(self):
		logging.debug("Shortcut F10 pushed")
				
		
	

		
app = QApplication(sys.argv)
app.setStyle("Fusion")													# required to use it here
mw = MainWindow()
app.exec_()
