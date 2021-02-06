
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
from labelled_animated_toggle import *

COLORS = ["ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"FFA500","7fff00","00ff7f","007FFF","EE82EE","FF007F",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"FFA500","7fff00","00ff7f","007FFF","EE82EE","FF007F",]

MAX_PLOTS = 12															# Absolute maximum number of plots, change if needed !!

		
class MyPlot(QWidget):
					
	n_plots = 12														# number of plots on the current plot. 
	plot_tick_ms = 50													# every "plot_tick_ms", the plot updates, no matter if there's new data or not. 
	dataset = []														# complete dataset, this should go to a file.							
	toggles = []														# references to the toggles which enable/disable plots.													
	
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

		self.set_enabled_graphs("none")									# writes to a variable of graph indicating which graphs are on
		
		print("Init until set_enabled_graphs")
		
		for toggle in self.toggles:
			toggle.setChecked(True)
			toggle.setEnabled(True)
		
		# ~ for toggle in self.toggles:
			# ~ print("IsChecked")
			# ~ print(toggle.isChecked())
			# ~ print("IsEnabled")
			# ~ print(toggle.isEnabled())
						
	def add_toggles(self):												# encapsulates the creation of the toggles, and their initial setup.
		for i in range(0, MAX_PLOTS):
			color = "#"+COLORS[i]
			label_toggle = LabelledAnimatedToggle(color = color)
			self.toggles.append(label_toggle)
			label_toggle.setChecked(False)						# all toggles not checked by default	# create new method to call the toggle method?
			label_toggle.setEnabled(True)						# all toggles not enabled by default
			self.layout_channel_select.addWidget(label_toggle)
			
	def enable_toggles(self,val):
		if(val == "all"):
			for i in range(MAX_PLOTS):
				self.toggles[i].setEnabled(True)
		elif(val == "none"):
			for i in range(MAX_PLOTS):
				self.toggles[i].setEnabled(False) 
		else:
			pass			# fill with behavior if val is a vector
		
	def check_toggles(self,vals):
		if(vals == "all"):
			for i in range(MAX_PLOTS):
				print(self.toggles[i].isEnabled())
				if(self.toggles[i].isEnabled()):						# so we can only check enabled toggles. 
					self.toggles[i].setChecked(True)
		elif(vals == "none"):
			for i in range(MAX_PLOTS):
				self.toggles[i].setChecked(False) 
		else:
			for i in range (MAX_PLOTS):
				self.toggles[i].setChecked(vals[i])						# vals should be a list with as many elements as toggles
		
	def set_channels_labels(self,names):								# each channel toggle has a label, set the text on that label.
		for i in range(MAX_PLOTS):										# we only assign the names of the plots that can be plotted
			try:
				self.toggles[i].setLabel(names[i])
			except Exception as e:
				logging.debug("more channels than labels")
				
	def clear_channels_labels(self):									# clear all labels, usually to set them with new vals.
		for i in range(MAX_PLOTS):										# we only assign the names of the plots that can be plotted
			try:
				self.toggles[i].setLabel('')
			except Exception as e:
				logging.debug("more channels than labels")
					

	def create_plots(self):
		self.graph.create_plots()

	def clear_plot(self):												# NOT WORKING 
		self.graph.clear_plot()

	def on_plot_timer(self):											# this is an option, to add together toggle processing and replot.
		enabled = []
		for i in range(0,MAX_PLOTS):
			if(self.toggles[i].toggle.isChecked()):
				enabled.append(True)
			else:
				enabled.append(False)		
			
		self.set_enabled_graphs(enabled)
		
		self.graph.dataset = self.dataset
						
		self.graph.on_plot_timer()										# calls the regular plot timer from graph.
		
	def plot_timer_start(self):											
		self.graph.timer.start()

	def update(self):													# notifies a change in the dataset
		self.graph.dataset_changed = True								# flag
		#self.graph.dataset = self.dataset
		
	def setBackground(self, color):
		self.graph.setBackground(color)

	def start_plotting(self, period = None):
		if(period == None):
			self.plot_timer.start()
		else:
			self.plot_timer.start(period)

	def stop_plotting(self):
		self.plot_timer.stop()

	def set_enabled_graphs(self, enable_list):
		if enable_list == "all":
			enable_list = []
			for i in range(MAX_PLOTS):
				enable_list.append(True)
		elif enable_list == "none":
			enable_list = []
			for i in range(MAX_PLOTS):
				enable_list.append(False)
		
		self.graph.set_enabled_graphs(enable_list)
						


class MyGraph(pg.PlotWidget):											# this is supposed to be the python convention for classes. 
	
	# Arduino serial plotter has 500 points max. on the x axis.
	max_points = None													# maximum points per plot
	tvec = []															# independent variable, with "max_points" points.			
	n_plots = 12														# number of plots on the current plot. 
	first = True														# first iteration only creating the plots
	
	dataset = None														# complete dataset, this should go to a file.	
	np_dataset = None													# used for reverting the matrix.
	np_dataset_t = None						
	plot_refs = []														# references to the different added plots.
	plot_subset = []
	enabled_graphs = []													# enabled graphs ON GRAPH WINDOW, not on toggles. 
	
	for i in range(0,MAX_PLOTS):
		enabled_graphs.append(False)									
													
	dataset_changed = False


	#dataset = np.array()
	
	def __init__(self, dataset = None, max_points = 500, title = ""):

		for i in range(max_points):										# create a time vector --> move to NUMPY !!!
			self.tvec.append(i)
		
		self.dataset = dataset											# get the reference to the dataset given as input for the constructor
		self.max_points = max_points
			
		#self.plot_subset = self.dataset[:self.n_plots][-(self.max_points):]	 # get only the portion of the dataset which needs to be printed. 	
			
		super().__init__()		
		pg.setConfigOptions(antialias=False)							# antialiasing for nicer view. 
		self.setBackground([70,70,70])									# changing default background color.
		self.showGrid(x = True, y = True, alpha = 0.5)
		self.setRange(xRange = [0,self.max_points], yRange = [-10,100]) 	# set default axes range
		self.setLimits(xMin=0, xMax=self.max_points, yMin=-1000, yMax=1000)	# THIS MAY ENTER IN CONFIG WITH PLOTTING !!!
		#self.enableAutoRange(axis='x', enable=True)						# enabling autorange for x axis
		legend = self.addLegend()
		self.setTitle(title)											# if title is wanted	
		
	def create_plots(self):
		for i in range (MAX_PLOTS):
			logging.debug("val of i:" + str(i))
			p = self.plot(pen = (COLORS[i%24]))
			self.plot_refs.append(p)


	def clear_plot(self):												
		print("clear_plot method called")
		for i in range(len(self.plot_subset)):
			self.plot_refs[i].clear()									# clears the plot
			self.plot_refs[i].setData([0])								# sets the data to 0, may not be necessary
			#self.plot_subset[i] = []
			
	def set_enabled_graphs(self,enabled_graphs):						# enabled/dsables graphs ON GRAPH WINDOW, not on the toggles.
		self.enabled_graphs = enabled_graphs

	
	def on_plot_timer(self):
		#print("PLOT_TIMER MyGraph")										
		#print (self.dataset_changed)	

		if self.first == True:											# FIRST: CREATE THE PLOTS 
			self.create_plots()	
			print("len(self.plot_refs)")
			print(len(self.plot_refs))
			self.first = False
			print("First plot timer")

		# SECOND: UPDATE THE PLOTS:
		
		if(self.dataset_changed == True):								# redraw only if there are changes on the dataset
			#print("dataset has changed")
			#print("length of subset")
			#print(len(self.plot_subset))
			self.dataset_changed = False
			
			self.np_dataset = np.matrix(self.dataset[:][-self.max_points:])		# we only use as subset the last max_points
			self.np_dataset_t = self.np_dataset.transpose()
			self.plot_subset = self.np_dataset_t.tolist()
			# ~ print("len(self.plot_subset[0])")
			# ~ print(len(self.plot_subset[0]))

			
			# ~ print("self.dataset")
			# ~ print(self.dataset)
			# ~ print("self.np_dataset")
			# ~ print(self.np_dataset)			
			# ~ print("self.plot_subset")
			# ~ for var in self.plot_subset:
				# ~ print(var)	

						
			for i in range(len(self.plot_subset)):
				# ~ print("len(self.plot_refs)")
				# ~ print(len(self.plot_refs))
				if(self.enabled_graphs[i] == True):
					self.plot_refs[i].setData(self.plot_subset[i]) 		# required for update: reassign references to the plots
				else:
					self.plot_refs[i].setData([])	# empty plot, if toggle not active.
				
				self.dataset_changed = True
			
			pg.QtGui.QApplication.processEvents()						# for whatever reason, works faster when using processEvent.
		

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

			self.plot.check_toggles("all")
			self.plot.enable_toggles("all")
								


			self.setCentralWidget(self.plot)
			# last step is showing the window #
			self.show()
			
			#self.plot.graph.plot_timer.start()
			
		
		def on_data_timer(self):										# simulate data coming from external source at regular rate.
			t0 = time.time()
			logging.debug("length of dataset: " + str(len(self.plot.dataset)))
			
			
			line = []
			for i in range(0,MAX_PLOTS):
					line.append(random.randrange(0,100))	
			self.dataset.append(line)
					
			print("self.dataset")
			for data in self.dataset:
				print(data)
			
			self.plot.dataset = self.dataset							# this SHOULD HAPPEN INTERNAL TO THE CLASS !!!
					
			self.plot.update()
			t = time.time()
			dt = t - t0
			logging.debug("execution time add_stuff_dataset " + str(dt))
			

	app = QApplication([])
	app.setStyle("Fusion")												# required to use it here
	mw = MainWindow()
	app.exec_()

