
import random
import time 
import logging

import numpy as np


from PyQt5.QtWidgets import(
	QApplication,
	QMainWindow
)

from PyQt5.QtCore import(
	QTimer
)
import pyqtgraph as pg


COLORS = ["ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",

]

MAX_PLOTS = 24															# Absolute maximum number of plots, change if needed !!


class MyGraph(pg.PlotWidget):											# this is supposed to be the python convention for classes. 
	
	# Arduino serial plotter has 500 points max. on the x axis.
	max_points = None													# maximum points per plot
	
	tvec = []															# independent variable, with "max_points" points. 
			
	n_plots = 12														# number of plots on the current plot. 
	first = True														# first iteration only creating the plots
	plot_tick_ms = 20													# every "plot_tick_ms", the plot updates, no matter if there's new data or not. 
	
	
	#dataset = []														# complete dataset, this should go to a file.							
	plot_refs = []														# references to the different added plots.
	plot_subset = []
													
	dataset_changed = False


	#dataset = np.array()
	
	def __init__(self, dataset = None, max_points = 500):

		for i in range(max_points):										# create a time vector --> move to NUMPY !!!
			self.tvec.append(i)
		
		self.dataset = dataset											# get the reference to the dataset given as input for the constructor
		self.max_points = max_points
		
			
		# ~ for i in range(self.max_plots):								# this is the section of the dataset which will be plotted (always 1000 points per set)
			# ~ self.plot_subset.append([])
			
		self.plot_subset = self.dataset[:self.n_plots][-(self.max_points):]	 # get only the portion of the dataset which needs to be printed. 	
		
		
		super().__init__()		
		pg.setConfigOptions(antialias=False)							# antialiasing for nicer view. 
		self.setBackground([70,70,70])									# changing default background color.
		#self.setBackground([125,125,125])								# changing default background color.
		self.showGrid(x = True, y = True, alpha = 0.5)
		# do something to set the default axes range
		#self.setRange(xRange = [0,1000], yRange = [-200,200])
		self.setRange(xRange = [0,self.max_points], yRange = [-1200,1200])
		self.setLimits(xMin=0, xMax=self.max_points, yMin=-1000, yMax=1000)	# THIS MAY ENTER IN CONFIG WITH PLOTTING !!!
		#self.enableAutoRange(axis='x', enable=True)						# enabling autorange for x axis
		#self.enableAutoRange(axis='y', enable = True)
		legend = self.addLegend()
		# self.setTitle("PENIS")
		
			
		self.plot_timer = QTimer()										# used to update the plot
		self.plot_timer.timeout.connect(self.on_plot_timer)				# 
		self.plot_timer.start(self.plot_tick_ms)						# will also control the refresh rate.	


	def create_plots(self):
		for i in range (len(self.plot_subset)):
			logging.debug("val of i:" + str(i))
			#p = self.plot(pen = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)),name ="Plot" + str(i))
			#p = self.plot(pen = (COLORS[i%24]),name ="Plot" + str(i))
			p = self.plot(pen = (COLORS[i%24]))
			self.plot_refs.append(p)

			self.first = False

	def clear_plot(self):												# NOT WORKING 
		print("clear_plot method called")
		for i in range(len(self.plot_subset)-1):
			self.plot_refs[i].clear()
			self.plot_refs[i].setData([0])
			self.plot_subset[i] = []
			
	
	def on_plot_timer(self):

		if self.first == True:											# FIRST: CREATE THE PLOTS 
			self.create_plots()	
		# SECOND: UPDATE THE PLOTS:
		
		if(self.dataset_changed == True):								# redraw only if there are changes on the dataset

			self.dataset_changed = False
			for i in range(len(self.plot_subset)):
				 self.plot_refs[i].setData(self.plot_subset[i], name = "small penis") 		# required for update: reassign references to the plots
				# self.plot_refs[i].setData(self.t, self.plot_subset[i])# required for update: reassign references to the plots
									
			for i in range(0,self.n_plots):		
				self.plot_subset[i] = self.dataset[i][-self.max_points:]	# gets the last "max_points" of the dataset.
			
			pg.QtGui.QApplication.processEvents()						# for whatever reason, works faster when using processEvent.
		


## THIS PART WON'T BE EXECUTED WHEN IMPORTED AS A SUBMODULE, BUT ONLY WHEN TESTED INDEPENDENTLY ##

if __name__ == "__main__":

	class MainWindow(QMainWindow):
		
		# class variables #
		data_tick_ms = 5

		#creating a fixed size dataset #
		dataset = []
	
		# constructor # 
		def __init__(self):
			
			super().__init__()

			# initializing empty dataset #
			for i in range(MAX_PLOTS):									# we're creating a dataset with an eXcess of rows!!!
				self.dataset.append([])	

			# add graph and show #
			self.graph = MyGraph(dataset = self.dataset)					# extend the constructor, to force giving a reference to a dataset ???

			
			self.data_timer = QTimer()
			self.data_timer.timeout.connect(self.on_data_timer)
			self.data_timer.start(self.data_tick_ms)


			self.setCentralWidget(self.graph)
			# last step is showing the window #
			self.show()

		def on_data_timer(self):										# simulate data coming from external source at regular rate.
			t0 = time.time()
			logging.debug("length of dataset: " + str(len(self.graph.dataset)))
			
			for i in range(0,MAX_PLOTS):
				for j in range(50):
					self.dataset[i].append(random.randrange(0,100))				
				
			self.graph.dataset_changed = True							# replace this for an update method call which changes a flag?
			t = time.time()
			dt = t - t0
			logging.debug("execution time add_stuff_dataset " + str(dt))

			try:
				self.graph.clear_plot()
			except:
				print("issue cleaning plot")
	
			

	app = QApplication([])
	app.setStyle("Fusion")												# required to use it here
	mw = MainWindow()
	app.exec_()

