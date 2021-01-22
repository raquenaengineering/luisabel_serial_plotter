
import random
import time 
import logging
import math

import numpy as np


from PyQt5.QtWidgets import(
	QApplication,
	QMainWindow,
	QWidget,
	QHBoxLayout,																# create a new widget, which contains the MyGraph window
	QVBoxLayout,
	QLabel
)

from PyQt5.QtCore import(
	QTimer
)
import pyqtgraph as pg
import qtwidgets

COLORS = ["ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"FFA500","7fff00","00ff7f","007FFF","EE82EE","FF007F",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"FFA500","7fff00","00ff7f","007FFF","EE82EE","FF007F",]

MAX_PLOTS = 12															# Absolute maximum number of plots, change if needed !!

class LabelledAnimatedToggle(QWidget):
	
	def __init__(self,color = "#aaffaa", label_text = ""):				# optional parameters instead ??? yes, thanks.
		super().__init__()
		self.label = QLabel(label_text)
		self.toggle = qtwidgets.AnimatedToggle(checked_color = color)
		
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)
		self.layout.addWidget(self.toggle)
		self.layout.addWidget(self.label)
		self.layout.setContentsMargins(0,0,0,0)							# reducing the space the toggle takes as much as possible	
		self.layout.setSpacing(0)
		
	def setLabel(self,label_text):
		self.label.setText(label_text)	
	def setChecked(self, val):
		self.toggle.setChecked(val)
	def setEnabled(self, val):
		self.toggle.setEnabled(val)
		

class MyPlot(QWidget):
	
	# Arduino serial plotter has 500 points max. on the x axis.
	max_points = None													# maximum points per plot
	
	tvec = []															# independent variable, with "max_points" points. 
			
	n_plots = 12														# number of plots on the current plot. 
	first = True														# first iteration only creating the plots
	plot_tick_ms = 20													# every "plot_tick_ms", the plot updates, no matter if there's new data or not. 
	
	
	dataset = []														# complete dataset, this should go to a file.							
	plot_refs = []														# references to the different added plots.
	toggles = []														# references to the toggles which enable/disable plots.
	enabled_graphs = []
	names_refs = []														# references with the names
	plot_subset = []
													
	dataset_changed = False	
	
	
	def __init__(self, dataset = [], max_points = 200):
		super().__init__()	
		
		# central widget #
		self.layout = QHBoxLayout()										# that's how we will lay out the window
		self.setLayout(self.layout)
		self.graph = MyGraph(dataset = dataset, max_points = max_points)
		self.layout.addWidget(self.graph)
		self.layout_channel_select = QVBoxLayout()
		self.layout.addLayout(self.layout_channel_select)
		self.channel_label = QLabel("Channels:")
		self.layout_channel_select.addWidget(self.channel_label)
		self.add_toggles()
				
		self.layout_channel_name = QVBoxLayout()
		# timer #
		self.plot_timer = QTimer()										# used to update the plot
		self.plot_timer.timeout.connect(self.on_plot_timer)				# 
		self.start_plotting(self.plot_tick_ms)
		self.stop_plotting()			
		
	def set_channels_labels(self,names):
		for i in range(MAX_PLOTS):										# we only assign the names of the plots that can be plotted
			try:
				self.toggles[i].setLabel(names[i])
			except Exception as e:
				logging.debug("more channels than labels")
				#print(e)		

	def clear_channels_labels(self):
		for i in range(MAX_PLOTS):										# we only assign the names of the plots that can be plotted
			try:
				self.toggles[i].setLabel('')
			except Exception as e:
				logging.debug("more channels than labels")
				#print(e)	
					
	def add_toggles(self):
		for i in range(0, MAX_PLOTS):
			color = "#"+COLORS[i]
			#print(color)			
			#label_toggle = LabelledAnimatedToggle()
			label_toggle = LabelledAnimatedToggle(color = color)
			self.toggles.append(label_toggle)
			label_toggle.setChecked(True)						# all toggles not checked by default	# create new method to call the toggle method?
			label_toggle.setEnabled(True)						# all toggles not enabled by default
			self.layout_channel_select.addWidget(label_toggle)

	def create_plots(self):
		self.graph.create_plots()

	def clear_plot(self):												# NOT WORKING 
		self.graph.clear_plot()

	def on_plot_timer(self):											# this is an option, to add together toggle processing and replot.
		#print("PLOT TIMER MyPlot")
		self.enabled_graphs = []
		for i in range(0,MAX_PLOTS):
			if(self.toggles[i].toggle.isChecked()):
				self.enabled_graphs.append(True)
			else:
				self.enabled_graphs.append(False)
			
		self.graph.enable_graphs(self.enabled_graphs)					# writes to a variable of graph indicating which graphs are on
		self.graph.on_plot_timer()										# calls the regular plot timer from graph.
		
	def plot_timer_start(self):											
		self.graph.timer.start()

	def update(self):													# 
		self.graph.dataset_changed = True
		
	def setBackground(self, color):
		self.graph.setBackground(color)

	def start_plotting(self, period = None):
		if(period == None):
			self.plot_timer.start()
		else:
			self.plot_timer.start(period)

	def stop_plotting(self):
		self.plot_timer.stop()

class MyGraph(pg.PlotWidget):											# this is supposed to be the python convention for classes. 
	
	# Arduino serial plotter has 500 points max. on the x axis.
	max_points = None													# maximum points per plot
	tvec = []															# independent variable, with "max_points" points.			
	n_plots = 12														# number of plots on the current plot. 
	first = True														# first iteration only creating the plots
	plot_tick_ms = 20													# every "plot_tick_ms", the plot updates, no matter if there's new data or not. 
	
	
	dataset = None														# complete dataset, this should go to a file.							
	plot_refs = []														# references to the different added plots.
	plot_subset = []
	active_graphs = []
	
	for i in range(0,MAX_PLOTS):
		active_graphs.append(False)
													
	dataset_changed = False


	#dataset = np.array()
	
	def __init__(self, dataset = None, max_points = 500, title = ""):

		for i in range(max_points):										# create a time vector --> move to NUMPY !!!
			self.tvec.append(i)
		
		self.dataset = dataset											# get the reference to the dataset given as input for the constructor
		self.max_points = max_points
			
		self.plot_subset = self.dataset[:self.n_plots][-(self.max_points):]	 # get only the portion of the dataset which needs to be printed. 	
			
		super().__init__()		
		pg.setConfigOptions(antialias=False)							# antialiasing for nicer view. 
		self.setBackground([70,70,70])									# changing default background color.
		self.showGrid(x = True, y = True, alpha = 0.5)
		self.setRange(xRange = [0,self.max_points], yRange = [-1200,1200]) # set default axes range
		self.setLimits(xMin=0, xMax=self.max_points, yMin=-1000, yMax=1000)	# THIS MAY ENTER IN CONFIG WITH PLOTTING !!!
		#self.enableAutoRange(axis='x', enable=True)						# enabling autorange for x axis
		legend = self.addLegend()
		self.setTitle(title)											# if title is wanted								

	def create_plots(self):
		for i in range (len(self.plot_subset)):
			logging.debug("val of i:" + str(i))
			p = self.plot(pen = (COLORS[i%24]))
			self.plot_refs.append(p)

			self.first = False

	def clear_plot(self):												# NOT WORKING 
		print("clear_plot method called")
		for i in range(len(self.plot_subset)):
			self.plot_refs[i].clear()									# clears the plot
			self.plot_refs[i].setData([0])								# sets the data to 0, may not be necessary
			#self.plot_subset[i] = []
			
	
	def on_plot_timer(self):
		#print("PLOT_TIMER MyGraph")										
		#print (self.dataset_changed)	

		if self.first == True:											# FIRST: CREATE THE PLOTS 
			self.create_plots()	
			self.first = False
			print("First plot timer")
		# SECOND: UPDATE THE PLOTS:
		
		if(self.dataset_changed == True):								# redraw only if there are changes on the dataset
			#print("dataset has changed")
			#print("length of subset")
			#print(len(self.plot_subset))
			self.dataset_changed = False
			for i in range(len(self.plot_subset)):
				#print(self.active_graphs[i])
				if(self.active_graphs[i] == True):
					self.plot_refs[i].setData(self.plot_subset[i], name = "small penis") 		# required for update: reassign references to the plots
					# self.plot_refs[i].setData(self.t, self.plot_subset[i])# required for update: reassign references to the plots
				else:
					self.plot_refs[i].setData([], name = "small penis")	# empty plot, if toggle not active.
				
									
			for i in range(0,self.n_plots):		
				self.plot_subset[i] = self.dataset[i][-self.max_points:]	# gets the last "max_points" of the dataset.
			
			pg.QtGui.QApplication.processEvents()						# for whatever reason, works faster when using processEvent.
		

	def enable_graphs(self, enable_list):	
		self.active_graphs = enable_list
		#for i in range(0,MAX_PLOTS):
						

## THIS PART WON'T BE EXECUTED WHEN IMPORTED AS A SUBMODULE, BUT ONLY WHEN TESTED INDEPENDENTLY ##

if __name__ == "__main__":

	class MainWindow(QMainWindow):
		
		# class variables #
		data_tick_ms = 20

		#creating a fixed size dataset #
		dataset = []
	
		# constructor # 
		def __init__(self):
			
			super().__init__()
			

			# initializing empty dataset #
			for i in range(MAX_PLOTS):									# we're creating a dataset with an eXcess of rows!!!
				self.dataset.append([])	

			# add graph and show #
			#self.graph = MyGraph(dataset = self.dataset)
			self.plot = MyPlot(dataset = self.dataset)					# extend the constructor, to force giving a reference to a dataset ???
			self.plot.set_channels_labels(["Gastro Medialis", 
											"Gastro Lateralis", 
											"Australopitecute",
											"caracol",
											"col",
											"pene",
											"carapene",
											"Ermengildo II",
											"mondongo",
											"cagarruta",
											"Zurullo",
											"caca"])

			self.plot.start_plotting()
			
			self.data_timer = QTimer()
			self.data_timer.timeout.connect(self.on_data_timer)
			self.data_timer.start(self.data_tick_ms)


			self.setCentralWidget(self.plot)
			# last step is showing the window #
			self.show()
			
			#self.plot.graph.plot_timer.start()
			
			

			
		def on_data_timer(self):										# simulate data coming from external source at regular rate.
			t0 = time.time()
			logging.debug("length of dataset: " + str(len(self.plot.dataset)))
			
			for j in range(50):
				self.dataset[0].append(50*math.sin(j/4) + 80)
			for i in range(1,MAX_PLOTS):
				for j in range(50):
					self.dataset[i].append(random.randrange(0,100))	
					
				
			self.plot.update()
			t = time.time()
			dt = t - t0
			logging.debug("execution time add_stuff_dataset " + str(dt))
			

	app = QApplication([])
	app.setStyle("Fusion")												# required to use it here
	mw = MainWindow()
	app.exec_()

