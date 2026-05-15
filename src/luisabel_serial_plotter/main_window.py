# standard imports #
import sys											# deal with OS, open files and so
import time 										# delays, and time measurement ?
import random										# random numbers
import os											# dealing with directories

import serial										# required to handle serial communication
import serial.tools.list_ports						# to list already existing ports

import csv
import numpy as np 										# required to handle multidimensional arrays/matrices

import logging
#logging.basicConfig(level=logging.DEBUG)			# enable debug messages
from future.utils import text_type

import parsers

logging.basicConfig(level = logging.WARNING)

# custom packages #

from pyqt_common_resources import pyqt_custom_palettes				# moved to an independent repo, to reuse the palettes.
from my_graph import MyPlot
import my_graph														# for the global variables of the namespace.
from re_pyqt_widgets.shortcuts_widget import ShortcutsWidget		# custom widget to display and edit shortcuts
from re_pyqt_widgets.socket_widget import socket_widget
from re_pyqt_widgets.serial_widget import serial_widget				# all serial is now handled by this widget
from range_dialog import RangeDialog

# qt imports #
from PySide6.QtWidgets import (
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
	QCheckBox,

	QSystemTrayIcon,
	QTextEdit,
	QMenu,
	QWidget,
	QInputDialog,
)

from PySide6.QtGui import (
	QIcon,
	QShortcut,
	QAction,

	QKeySequence
)

from PySide6.QtCore import(
	Qt,
	QThreadPool,
	QRunnable,
	QObject,
	QSize,
	Signal,															# those two are pyqt specific.
	Slot,
	QTimer																# nasty stuff

)

# GLOBAL VARIABLES #

SERIAL_BUFFER_SIZE = 10000												# buffer size to store the incoming data from serial, to afterwards process it.
SEPARATOR = "----------------------------------------------------------"

DATA_PERIOD = 1000
RECORD_PERIOD = 1000 													# time in ms between two savings of the recorded data onto file
POINTS_PER_PLOT = 2000													# width of x axis, corresponding to the number of dots to be plotted at each iteration


# THREAD STUFF #  (not needed ATM)

		
# MAIN WINDOW #			

class MainWindow(QMainWindow): 
	"""
	Main window of our application:
	Contains:
	serial_widget
		- buttons
		- log window
	socket_wiget		--> hidden by default, when changing to socket view, hide serial_widget instead.
		- buttons
		- log window
	plot_graph
	"""

	PERIOD_DATA_TIMER = DATA_PERIOD
	PERIOD_RECORD_TIMER = RECORD_PERIOD

	error_type = None													# used to try to fix the problem with dialog window, delete if can't fix !!!
	serial_message_to_send = None										# if not none, is a message to be sent via serial port (the worker sends)
	full_screen_flag = False											# to handle full screen with shortcuts
	dataset = []														# dataset containing the data to be plotter/recorded. DO I REALLY NEED THIS DATASET HERE; OR CAN I SIMPLY RELAY ON THE DATASET OF PLOT/GRAPH?
	log_folder = "logs"													# in the beginning, log folder, path and filename are fixed
	log_file_name = "log_file"											# at some point, path needs to be selected by user.
	log_file_type = ".csv"												# file extension
	n_logs = 0															# ???
	log_full_path = None												# this variable will be the one used to record 
	timeouts = 0														# ???
	parsing_style = "arduino"											# defines the parsing style, for now Arduino, or EMG
	read_buffer = ""													# if change to default parsing emg style: read_buffer = [], all chars read from serial come here, should it go somewhere else?
	recording = False													# flag to start/stop recording.
	first_toggles = 0													# used to check the toggles which contain data on start graphing.
	n_data_points = POINTS_PER_PLOT										# defaults to the POINTS_PER_PLOT value
	parser = parsers.parsers()											# create a parser to use it later on

	# constructor # 
	def __init__(self):
				
		super().__init__()
		
		self.init_dataset()


		# data input timer, every fixed time checks for new data #
		# self.data_timer = QTimer()										# we'll use timer instead of thread
		# self.data_timer.timeout.connect(self.on_data_timer)				# connect with callback
		# self.data_timer.start(self.PERIOD_DATA_TIMER)					# period needs to be relatively short
		# self.data_timer.stop()										# by default the timer will be off, enabled by connect.



		# timer to record data onto file periodically (DELETES OLD DATA IF RECORD NOT ENABLED)#
		self.record_timer = QTimer()
		self.record_timer.timeout.connect(self.on_record_timer)			# will be enabled / disabled via button
		self.record_timer.start(self.PERIOD_RECORD_TIMER)				# deploys data onto file once a second
		self.record_timer.stop()



		# shortcuts moved to the bottom #

		# theme(palette) #
		self.palette = pyqt_custom_palettes.dark_palette()
		self.setPalette(self.palette)
		
		# window stuff #
		self.setWindowTitle("Luisabel Plotter")							# relevant title
		self.setWindowIcon(QIcon("RE_logo_32p.png"))					# basic raquena engineering branding
		self.resize(1200,800)											# setting initial window size
		# menubar #
		menu = self.menuBar()											# by default, the window already has an instance/object menubar
		# file #
		self.file_menu = menu.addMenu("&File")
		# Preferences #
		self.preferences_menu = menu.addMenu("&Preferences")
		# Communication #
		self.parsing_submenu = self.preferences_menu.addMenu("Communication")
		self.arduino_parsing_option = self.parsing_submenu.addAction("Serial")
		self.arduino_parsing_option.triggered.connect(self.set_serial_widget)
		self.emg_parsing_option = self.parsing_submenu.addAction("Socket")
		self.emg_parsing_option.triggered.connect(self.set_socket_widget)
		# theme #
		self.theme_submenu = self.preferences_menu.addMenu("Theme")
		self.dark_theme_option = self.theme_submenu.addAction("Dark")
		self.dark_theme_option.triggered.connect(self.set_dark_theme)
		self.light_theme_option = self.theme_submenu.addAction("Light")
		self.light_theme_option.triggered.connect(self.set_light_theme)
		self.re_theme_option = self.theme_submenu.addAction("Raquena")
		self.re_theme_option.triggered.connect(self.set_re_theme)
		# Parsing #
		self.parsing_submenu = self.preferences_menu.addMenu("Parsing mode")
		self.arduino_parsing_option = self.parsing_submenu.addAction("Arduino")
		self.arduino_parsing_option.triggered.connect(self.set_arduino_parsing)
		self.emg_parsing_option = self.parsing_submenu.addAction("EMG Sensor")
		self.emg_parsing_option.triggered.connect(self.set_emg_parsing)
		self.emg_parsing_new_option = self.parsing_submenu.addAction("EMG Sensor NEW")
		self.emg_parsing_new_option.triggered.connect(self.set_emg_parsing_new)
		# Set plot range #
		self.set_range_action = self.preferences_menu.addAction("Set Plot Y Range")
		self.set_range_action.triggered.connect(self.set_plot_range)
		# Set maximum plot points #
		self.set_n_plot_points_action = self.preferences_menu.addAction("Set max. plot points (X Range)")
		self.set_n_plot_points_action.triggered.connect(self.set_n_plot_points)
		# shortcuts #
		self.shortcuts_action = self.preferences_menu.addAction("Shortcuts")
		self.shortcuts_action.triggered.connect(self.shortcut_preferences)
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
		self.layout_plot = QHBoxLayout()								# plot plus buttons to enable/disable graphs
		self.layoutV1.addLayout(self.layout_plot)
		self.plot_frame = MyPlot(dataset = self.dataset, 
									max_points = self.n_data_points)		# we'll use a custom class, so we can modify the defaults via class definition
		self.plot_frame.max_points = self.n_data_points					# width of the plot in points, doesn't work !!!
		self.plot_frame.enable_toggles("none")
		self.plot_frame.check_toggles("none")
		self.layout_plot.addWidget(self.plot_frame)
		self.plot_frame.setVisible(True)


		## THIS TO A NEW WIDGET ??? ##
		# buttons for plot #
		self.layout_player = QHBoxLayout()
		self.layoutV1.addLayout(self.layout_player)
		# play button # 
		self.button_play = QPushButton("Play")
		self.button_play.setIcon(QIcon('resources/player_icons/131.png'))
		self.button_play.clicked.connect(self.on_button_play)
		self.button_play.setEnabled(False)
		self.layout_player.addWidget(self.button_play)
		# pause button # 
		self.button_pause = QPushButton("Pause")
		self.button_pause.setIcon(QIcon('resources/player_icons/141.png'))
		self.button_pause.clicked.connect(self.on_button_pause)
		self.button_pause.setEnabled(True)
		self.layout_player.addWidget(self.button_pause)
		# record button # 
		self.button_record = QPushButton("Record")
		self.button_record.setIcon(QIcon('resources/player_icons/148.png'))
		self.button_record.clicked.connect(self.on_button_record)		# enables timer to periodically store the data onto a file. 
		self.layout_player.addWidget(self.button_record)		
		# stop button # 
		self.button_stop = QPushButton("Stop")
		self.button_stop.setIcon(QIcon('resources/player_icons/142.png'))
		self.button_stop.clicked.connect(self.on_button_stop)			# enables timer to periodically store the data onto a file. 
		self.button_stop.setEnabled(False)
		self.layout_player.addWidget(self.button_stop)
		# autoscale #
		self.button_autoscale = QPushButton("Scale Fit")
		self.button_autoscale.setIcon(QIcon('resources/player_icons/195.png'))
		self.button_autoscale.clicked.connect(self.on_button_autoscale)
		self.layout_player.addWidget(self.button_autoscale)
		#self.button_autoscale.setCheckable(True)

		# ~ self.autoscale_toggle = LabelledAnimatedToggle(color = "#ffffff",label_text = "Autoscale")
		# ~ self.layout_player.addWidget(self.autoscale_toggle)

		# SERIAL WIDGET #
		self.terminal_widget = serial_widget()
		# self.terminal_widget = socket_widget()
		self.terminal_widget.new_lines.connect(self.on_data_lines)
		self.layoutV1.addWidget(self.terminal_widget)

		####################################################################

		
		# status bar #
		self.status_bar = QStatusBar()
		self.setStatusBar(self.status_bar)
		self.status_bar.showMessage("Not Connected")
		# 3. write text saying no serial port is connected
		
		# show and done #		
		self.show()

	# on close #

	def closeEvent(self, event):

		print("CLOSING AND CLEANING UP:")
		try:
			self.terminal_widget.closeEvent()		# UNIMPLEMENTED --> SEND TO THE WIDGETS TO DEALY WITH IT.
		except:
			# print("Couldn't close serial port, probably already closed / never open")
			pass
		super().close()
		#event.ignore()													# extremely useful to ignore the close event !


	# actions #		
	
	def set_logfile(self):	
		"""
		Every time the record button is pressed, a new log file is created
		This method is in charge of creating the folder where the log files 
		will be saved, and each of the log files.
		:return: None
		"""
		# 1. be sure the folder where the log file should be placed exists
		# logs folder #
		print("Log file name:")
		print(self.log_file_name)
		print("Log file folder:")
		print(self.log_folder)
		
		if not os.path.exists(self.log_folder):							# create logs folder to store the logs
			os.makedirs(self.log_folder)								# mkdir only makes one directory on the path, makedirs, makes all
		# 2. check what's on that folder.
		path = os.getcwd()
		print("current path:")
		print(path)
		fullpath = path +'/'+ self.log_folder +'/'+ self.log_file_name + self.log_file_type
		print("Full file path")
		print(fullpath)
		if os.path.exists(fullpath):
			fullpath = path +'/'+ self.log_folder +'/'+ self.log_file_name + str(self.n_logs) + self.log_file_type
			self.n_logs = self.n_logs + 1
		
		self.log_full_path = fullpath;

	
	# other methods #

	# Buttons for pausing the graph and recording data #

	def on_button_pause(self):
		"""
		Pauses the plot
		so stops the update timer
		Also updates buttons enabled correspondingly
		:return:
		"""
		print("on_button_pause method: ")
		#self.plot_frame.plot_timer.stop()								# but we won't be able to rearm...
		self.plot_frame.stop_plotting()
		self.button_pause.setEnabled(False)
		self.button_play.setEnabled(True)
		
	def on_button_play(self):
		"""
		Starts running the plot again
		so starts the timer
		And also updates buttons enabled correspondingly
		:return:
		"""
		print("on_button_play method: ")
		self.button_play.setEnabled(False)
		self.button_pause.setEnabled(True)
		#self.plot_frame.plot_timer.start()								# but we won't be able to rearm...
		self.plot_frame.start_plotting()

	def on_button_record(self):
		print("on_button_record method: ")
		self.start_recording()
		self.set_logfile()
		self.button_record.setEnabled(False)
		self.button_stop.setEnabled(True)

	def on_button_stop(self):
		print("on_button_stop method: ")
		self.stop_recording()				
		#self.log_file.close()
		self.button_stop.setEnabled(False)
		self.button_record.setEnabled(True)
		
	def on_button_autoscale(self):
		# if self.button_autoscale.isChecked():							# if checked, we uncheck and disable autoscale.
			print("Autorange enabled")
			self.plot_frame.graph.enableAutoRange(axis='y')
			self.plot_frame.graph.setAutoVisible(y=True)				# don't know what's this
			#self.button_autoscale.setChecked(True)

		# else:
		# 	print("Autorange disabled")
		# 	self.button_autoscale.setEnabled(True)
		# 	self.button_autoscale.setChecked(False)


	# methods for keyboard shortcuts #

	def on_arrow_up(self):
		print("on_arrow_up method called")
		# change y axis from plot
		y_axis = self.plot_frame.graph.getAxis('left').range
		print(y_axis)
		for i in range(len(y_axis)):
			y_axis[i] = y_axis[i]/2
		self.plot_frame.graph.setRange(yRange = y_axis)
		
	def on_arrow_down(self):
		print("on_arrow_down method called")		
		# change y axis from plot
		y_axis = self.plot_frame.graph.getAxis('left').range
		print(y_axis)
		for i in range(len(y_axis)):
			y_axis[i] = y_axis[i]*2
		self.plot_frame.graph.setRange(yRange = y_axis)		
	
	def on_arrow_left(self):
		print("on_arrow_left method called")
		x_axis = self.plot_frame.graph.getAxis('bottom').range
		print(x_axis)
		for i in range(len(x_axis)):
			x_axis[i] = x_axis[i]/2
		self.plot_frame.graph.setRange(xRange = x_axis)			

	def on_arrow_right(self):
		print("on_arrow_right method called")
		x_axis = self.plot_frame.graph.getAxis('bottom').range
		print(x_axis)
		for i in range(len(x_axis)):
			x_axis[i] = x_axis[i]*2
		self.plot_frame.graph.setRange(xRange = x_axis)	

	def start_recording(self):
		"""
		Called when pressing record button
		sets the file where the data will be saved
		sets the recording flag, so  when on_record_timer is  called, data is stored to file.
		:return:
		"""
		self.set_logfile()
		self.recording = True
		
	def stop_recording(self):
		"""
		Called when stop button is pressed
		Resets recording flag, so no more data is stored.
		:return:
		"""
		self.recording = False

	def on_record_timer(self):
		"""
		Callback for the record timer.
		When in recording mode, stores the data into a file.
		:return: None
		"""
		#print("on_record_timer method called:")
		# t0 = time.time()

		if(self.recording == True):
			print("saving data to file")
			# ~ np_data = np.array(self.dataset)
			# ~ np_data_t = np_data.transpose()
			# ~ print("Data")
			# ~ print(np_data)
			# ~ print(SEPARATOR)
			# ~ print("Transposed data")
			# ~ print(np_data_t)
			# ~ print(SEPARATOR)
			with open(self.log_full_path, mode = 'a', newline = '') as csv_file:	# "log_file.csv" if will probably smash the data after first write!!!
				dataset_writer = csv.writer(csv_file, delimiter = ',')				# standard way to write to csv file
				for value in self.dataset[0:self.n_data_points]:						# only record the first "POINT_PER_PLOT" data points.
					dataset_writer.writerow(value)
		
		# t = time.time()
		# dt = t-t0
		# print(dt)
		# print(SEPARATOR)
		#
		# print("dataset lenght[0] on_record_timer():")
		# print(len(self.dataset))										# we need to use the first item, as dataset will have a lenght depending on the number of plots received from Arduino.
		# print("dataset lenght on_timer")

		# WHAT IS THIS? THIS IS PART OF THE RECORD ???
		while(len(self.dataset) > 3*self.n_data_points):						# this ensures there's always enough data to plot the whole window.
			logging.warning("Dataset removing some points")
			# ~ for i in range(self.n_data_points-1):
				# ~ self.dataset.pop()
			logging.debug(len(self.dataset))
			self.dataset = self.dataset[self.n_data_points:]					# removes the first "self.n_data_points" values from the dataset.
			logging.debug(len(self.dataset))
			self.plot_frame.dataset = self.dataset
			#self.clear_dataset()	# doesn't make any difference
			self.plot_frame.dataset_changed = True								# if we remove a part of the dataset, it is indeed changing.
			logging.debug("dataset_length after removing some points")
			logging.debug(len(self.dataset))

	def on_data_lines(self, lines):
		labels_changed = False

		for line in lines:
			labels, values = self.parser.arduino_parser((line + "\n").encode("utf-8"))

			if labels:
				self.plot_frame.set_channels_labels(labels)
				labels_changed = True

			if values:
				rows = list(map(list, zip(*values)))
				for row in rows:
					self.add_values_to_dataset(row)

		if labels_changed or lines:
			self.plot_frame.dataset = self.dataset
			self.plot_frame.update()

	"""
	HOW DOES IT COME ALL THESE METHODS DONT HAVE DOCUMENTATION ?
	"""
	def add_values_to_dataset(self,values):
		# print("values =")
		# print(values)
		self.dataset.append(values)  # appends all channels together
		# enabling corresponding toggles #
		for i in range(my_graph.MAX_PLOTS):  # this may not be the greatest option. it's fine.
			try:
				a = values[i]  # should crash after 4th element CHEAP FIX, MAKE IT BETTER !!!
				# self.dataset[i].append(valsf[i])				# if valsf has only 4 elements, it will throw error at 5th
				self.plot_frame.toggles[i].setEnabled(True)  # enable all graphs conataining data

				if (
					self.first_toggles <= 2):  # THIS SHOULD BE IF NO DATA ON DATASET[I], OR ONLY ONE ELEMENT ON DATASET[I]
					self.plot_frame.toggles[i].setChecked(True)
			except:
				pass

		self.first_toggles = self.first_toggles + 1				# ???

	def split_number_array(self, array, separator):
		results = []
		res = []
		for val in array:
			# print(res)
			# print(val)
			if val is not separator:
				res.append(val)
			else:
				results.append(res)
				res = []
		results.append(res)  # what's left on the res after the separator

		return(results)


		#num = int.from_bytes(byte, byteorder='big', signed=False)  # decoding to store in file

	def init_dataset(self):
		self.dataset = []

	def clear_dataset(self):	
		# initializing empty dataset #
		self.dataset = []

	def on_port_error(self,e):											# triggered by the serial thread, shows a window saying port is used by sb else.

		desc = str(e)
		logging.debug(type(e))
		logging.debug(desc)
		error_type = None
		i = desc.find("Port is already open.")
		if(i != -1):
			print("PORT ALREADY OPEN BY THIS APPLICATION")
			error_type = 1
			logging.debug(i)	
		i = desc.find("FileNotFoundError")
		if(i != -1):
			logging.debug("DEVICE IS NOT CONNECTED, EVEN THOUGH PORT IS LISTED")
			error_type = 2										# 
		i = desc.find("PermissionError")
		if(i != -1):
			logging.debug("SOMEONE ELSE HAS OPEN THE PORT")
			error_type = 3									# shows dialog the por is used (better mw or thread?) --> MW, IT'S GUI.
		
		i = desc.find("OSError")
		if(i != -1):
			logging.debug("BLUETOOTH DEVICE NOT REACHABLE ?")	
			error_type = 4
			
		i = desc.find("ClearCommError")
		if(i != -1):
			logging.debug("DEVICE CABLE UNGRACEFULLY DISCONNECTED")	
			error_type = 5



		# ~ i = desc.find("'utf-8' codec can't decode byte")			# NOT WORKING !!! (GIVING MORE ISSUES THAN IT SOLVED)
		# ~ if(i != -1):
			# ~ logging.debug("WRONG SERIAL BAUDRATE?")	
			# ~ error_type = 6

		self.error_type = error_type
		
		# ~ logging.debug("Error on serial port opening detected: ")
		# ~ logging.debug(self.error_type)
		self.handle_errors_flag = True									# more global variables to fuck things up even more. 
		self.handle_port_errors()
		
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
		if(self.error_type == 5):										# this means device not connected
			logging.warning("ERROR TYPE 5")
			d = QMessageBox.critical(
				self,
				"Serial Cable disconnected while transmitting",
				"Serial device was ungracefully disconnected, please check the cables",
				buttons=QMessageBox.Ok
			)
		if(self.error_type == 6):										# this means device not connected
			logging.warning("ERROR TYPE 6")
			d = QMessageBox.critical(
				self,
				"Serial wrong decoding",
				"There are problems decoding the data\n probably due to a wrong baudrate.",
				buttons=QMessageBox.Ok
			)
		self.on_button_disconnect_click()							# resetting to the default "waiting for connect" situation
		self.handle_errors_flag = False				
		self.error_type = None											# cleaning unhnandled errors flags. 


	def set_serial_widget(self):
		print("Setting serial widget for communication")
		self.set_terminal_widget(serial_widget)

	def set_socket_widget(self):
		print("Setting socket widget for communication")
		self.set_terminal_widget(socket_widget)


	def set_terminal_widget(self, widget_class):
		"""
		It is possible to change between serial and socket widget in execution time.
		This method is in charge of dealing with all actions required to do so
		widget_class: Either serial or socket
		"""

		if isinstance(self.terminal_widget, widget_class):			# if comm type not changed, do nothing.
			return

		# disabling old widget and saving state data #
		old_widget = self.terminal_widget							# keeps the old widget
		log_window_enabled = old_widget.check_log.isChecked()		# saves state of log checkbox, to keep it after widget change.

		try:
			old_widget.new_lines.disconnect(self.on_data_lines)		# disconnect old signal of incoming data lines
		except:
			pass

		try:
			if old_widget.button_disconnect.isEnabled():			# in case there is an open communication (connected)
				old_widget.on_button_disconnect_click()				# close the open connection
		except:
			pass

		# safely removing the old widget #
		self.layoutV1.removeWidget(old_widget)						# remove from layout
		old_widget.setParent(None)									# take out of the qt tree
		old_widget.deleteLater()									# marked to be deleted by pyqt

		# creating the new widget and attaching its signals #
		self.terminal_widget = widget_class(log_window=log_window_enabled)
		self.terminal_widget.new_lines.connect(self.on_data_lines)
		self.layoutV1.addWidget(self.terminal_widget)
		self.status_bar.showMessage("Not Connected")

	# check all themes and use lambda functions may be an option to use more themes #
	def set_dark_theme(self):
		self.palette = pyqt_custom_palettes.dark_palette()
		self.setPalette(self.palette)
		self.plot_frame.setBackground([60,60,60])
		
	def set_light_theme(self):
		self.palette = pyqt_custom_palettes.light_palette()
		self.setPalette(self.palette)
		self.plot_frame.setBackground([220,220,220])

	def set_re_theme(self):
		self.palette = pyqt_custom_palettes.re_palette()
		self.setPalette(self.palette)

	def set_arduino_parsing(self):
		self.read_buffer = ""
		self.parsing_style = "arduino"

	def set_emg_parsing(self):
		self.read_buffer = []
		self.parsing_style = "emg"

	def set_emg_parsing_new(self):
		self.read_buffer = []
		self.parsing_style = "emg_new"

	def set_plot_range(self):
		logging.debug("set_range_action method called")
		plot_range_dialog = RangeDialog()

		if plot_range_dialog.exec_():
			print(plot_range_dialog.getInputs())
			self.plot_frame.graph.setLimits(yMin=int(plot_range_dialog.getInputs()[0]),
											yMax=int(plot_range_dialog.getInputs()[1]))

	def set_n_plot_points(self):
		print("set_n_plot_points method called")
		i, okPressed = QInputDialog.getText(self, "Set n points", "Number of plot points (recommended max. 5000):")
		if okPressed:
			self.n_data_points = int(i)
			self.plot_frame.set_max_points(self.n_data_points)

	def shortcut_preferences(self):
		self.shortcuts = ShortcutsWidget()							# needs to be self, or it won't persist
		#0. should be done on init(): Load the shortcuts from a file where they're stored ¿in json format?
		#1. get the current shortcuts (stored somewhere in a variable, which also needs to be created(USE DICTIONARY))
		#2. create a widget containing a table with all the shortcuts and their shortcut value. 
		#

	def full_screen(self):												# it should be able to be detected from window class !!!
		if self.full_screen_flag == False:								
			self.showFullScreen()
			self.full_screen_flag = True
			logging.debug("Full Screen ENABLED")
		else:
			self.showNormal()
			self.full_screen_flag = False
			logging.debug("Full Screen DISABLED")
	
	# KEYPRESS HANDLER FOR SHORTCUTS ####
	def keyPressEvent(self, event):
		if not event.isAutoRepeat():
			print(event.text())	
			# FULL SHORTCUT LIST #	
			# arrows#
			if event.key() == Qt.Key_Up:
				self.on_arrow_up()
			elif event.key() == Qt.Key_Down:
				self.on_arrow_down()	
			elif event.key() == Qt.Key_Left:
				self.on_arrow_left()
			elif event.key() == Qt.Key_Right:
				self.on_arrow_right()
			#letters#
			elif event.text() == 'f':
				self.full_screen()
			elif event.text() == 'c':
				self.terminal_widget.on_button_connect_click()
			elif event.text() == 'd':
				self.terminal_widget.on_button_disconnect_click()
			elif event.text() == 'u':
				self.terminal_widget.update_serial_ports()
			elif event.text() == 'p':
				self.on_button_pause()
			elif event.text() == 'y':
				self.on_button_play()
			elif event.text() == 'r':
				self.on_button_record()	
			elif event.text() == 's':
				self.on_button_autoscale()
			elif event.text() == 'l':
				self.terminal_widget.check_log.toggle()
			# numbers #
			elif event.text() == '>':
				print("enable all")
				self.plot_frame.check_toggles("all")					# this can't be done 
			elif event.text() == '<':									# toggles plots all/none
				self.plot_frame.check_toggles("none")

			# plot channel toggles #
			elif event.key() >= Qt.Key_1 and event.key() <= Qt.Key_9:
				toggle_index = event.key() - Qt.Key_1
				if toggle_index < len(self.plot_frame.toggles):
					toggle = self.plot_frame.toggles[toggle_index]
					if toggle.isEnabled():
						toggle.toggle.toggle()							# review syntax in labelled_animated_toggle !!!

			elif event.key() == Qt.Key_0:
				toggle_index = 9
				if toggle_index < len(self.plot_frame.toggles):
					toggle = self.plot_frame.toggles[toggle_index]
					if toggle.isEnabled():
						toggle.toggle.toggle()
			# ctrl + #
			# communication shortcuts #
			if event.key() == Qt.Key_K and event.modifiers() & Qt.ControlModifier:
				self.set_socket_widget()

			elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
				self.set_serial_widget()

	# THIS DOESNT BELONG TO THE PLOTTER ################## !!!
	# def init_emg_sensor(self):
	# 	# initialization stuff (things required for the sensors to start sending shit)
	# 	# message = "E=1;"														# enable EMG data.
	# 	# self.serial_message_to_send = message.encode('utf-8')					# this should have effect on the serial_thread
	# 	# logging.debug(self.serial_message_to_send)
	# 	# self.serial_port.write(self.serial_message_to_send)
	# 	# message = "START;"
	# 	# self.serial_message_to_send = message.encode('utf-8')					# this should have effect on the serial_thread
	# 	# logging.debug(self.serial_message_to_send)
	# 	# self.serial_port.write(self.serial_message_to_send)
	# 	pass

										
if __name__ == '__main__':
		
	app = QApplication(sys.argv)
	app.setStyle("Fusion")													# required to use it here
	mw = MainWindow()
	app.exec()



