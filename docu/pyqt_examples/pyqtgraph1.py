
import random
import time 

import logging

from PyQt5.QtWidgets import(
	QApplication,
	QMainWindow
)

from PyQt5.QtCore import(
	QTimer
)
import pyqtgraph as pg


class MyGraph(pg.PlotWidget):
	
	# Arduino serial plotter has 500 points max. on the x axis.
	max_points = 2000													# maximum points per plot
	
	max_plots = 4														# maximum number of plots
	first = True														# first iteration only creating the plots
	plot_tick_ms = 1													# every "plot_tick_ms", the plot updates, no matter if there's new data or not. 
	
	
	dataset = []														# complete dataset, this should go to a file.							
	plot_refs = []														# references to the different added plots.
	plot_subset = []
													
	dataset_changed = False


	#dataset = np.array()
	
	def __init__(self):
		
			# creating a fixed size dataset #
		for i in range(self.max_plots):
			self.dataset.append([])
			
		for i in range(self.max_plots):									# this is the section of the dataset which will be plotted (always 1000 points per set)
			self.plot_subset.append([])
			
		
		
		super().__init__()		
		pg.setConfigOptions(antialias=False)								# antialiasing for nicer view. 
		self.setBackground([70,70,70])									# changing default background color.
		#self.setBackground([125,125,125])								# changing default background color.
		self.showGrid(x = True, y = True, alpha = 0.5)
		# do something to set the default axes range
		#self.setRange(xRange = [0,1000], yRange = [-200,200])
		self.setRange(xRange = [0,50], yRange = [0,256])
		self.setLimits(xMin=-10, xMax=100000, yMin=-1000, yMax=1000)	# THIS MAY ENTER IN CONFIG WITH PLOTTING !!!
		self.enableAutoRange(axis='x', enable=True)						# enabling autorange for x axis
		legend = self.addLegend()
		
		self.plot_timer = QTimer()										# used to update the plot
		self.plot_timer.timeout.connect(self.on_plot_timer)				# 
		self.plot_timer.start(self.plot_tick_ms)						# will also control the refresh rate.	

	
	def on_plot_timer(self):
		
		t0 = time.time()
			
		if self.first == True:
			# FIRST: CREATE THE PLOTS 
			# bring this to the graph creator 
			logging.debug("Add graph.plots_method called")
		
			#for dataplot in self.dataset:
			for i in range (len(self.dataset)):
				logging.debug("val of i:" + str(i))
				#p = self.plot(self.dataset[i], pen = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)),name ="Plot" + str(i))
				p = self.plot(self.plot_subset[i], pen = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)),name ="Plot" + str(i))
				self.plot_refs.append(p)

			self.first = False
		# SECOND: UPDATE THE PLOTS:
		
		# ~ for data_line in self.dataset:
			# ~ print(data_line)
		
		# ~ for data_line in self.plot_subset:
			# ~ print(data_line)
		
		
		if(self.dataset_changed == True):											# redraw only if there are changes on the dataset

			self.dataset_changed = False
			for i in range(len(self.dataset)):
				self.plot_refs[i].setData(self.plot_subset[i]) 
				
			pg.QtGui.QApplication.processEvents()
				
		t = time.time()
		dt = t - t0
		logging.debug("execution time on_plot_timer: " + str(dt))		

class MainWindow(QMainWindow):
	
	# class variables #
	data_tick_ms = 1
	
	
	# constructor # 
	def __init__(self):
		
		super().__init__()
		
		self.data_timer = QTimer()
		self.data_timer.timeout.connect(self.on_data_timer)
		self.data_timer.start(self.data_tick_ms)

		# add graph and show #
		self.graph = MyGraph()
		self.setCentralWidget(self.graph)
		# last step is showing the window #
		self.show()

	def on_data_timer(self):											# this indeed, should come from an external source !!!
		t0 = time.time()
		logging.debug("length of dataset: " + str(len(self.graph.dataset)))
		self.graph.dataset[0].append(25)								# does the dataset belong to the graph, or only the plot_subset ??? --> only plot_subset --> next fix iteration.
		for i in range(1,self.graph.max_plots):
			for j in range(50):
				self.graph.dataset[i].append(random.randrange(0,100))
			try:	
				self.graph.plot_subset[i] = []
				
				for j in range(len(self.graph.dataset[i])-(self.graph.max_points-1),(len(self.graph.dataset[i]))):
					self.graph.plot_subset[i].append(self.graph.dataset[i][j])
			except Exception as e :
				print(e)
			
			
		self.graph.dataset_changed = True
		t = time.time()
		dt = t - t0
		logging.debug("execution time add_stuff_dataset " + str(dt))
		

app = QApplication([])
app.setStyle("Fusion")													# required to use it here
mw = MainWindow()
app.exec_()
