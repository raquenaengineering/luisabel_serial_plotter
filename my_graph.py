
import logging
import random
import time

import numpy as np

from labelled_animated_toggle import *

COLORS = ["#ff0000","#00ff00","#0000ff","#ffff00","#ff00ff","#00ffff",
			"#FFA500","#7fff00","#00ff7f","#007FFF","#EE82EE","#FF007F",
			"#ff0000","#00ff00","#0000ff","#ffff00","#ff00ff","#00ffff",
			"#FFA500","#7fff00","#00ff7f","#007FFF","#EE82EE","#FF007F",]


MAX_PLOTS = 12															# Absolute maximum number of plots, change if needed !!
ABS_Y_MAX = 1000000														# Absolute maximum Y range, is fixed, and can only be changed on compilation time.
DEFAULT_Y_MAX = 100000													# max y by default (reachable when scrolling)
DEFAULT_Y_MIN = -100000													# min y by default
DEFAULT_MAX_POINTS = 2000												# number of points to be shown by default
CHANNEL_LABEL_MAX_LEN = 20												# limits the lenght of the channel label.


## GET BETTER NAMING FOR THIS !!! ##
class MyGraph(pg.PlotWidget):  # this is supposed to be the python convention for classes.
	"""
	Class containing the plot canvas plus everything else required to do a real time plot:
	This class has its own timer in order to update the graph at a regular basis, and flags to update only if there's new data.
	(It would be also possible to implement it in such a way that updates only if there's new data, consider that change)
	Also contains the whole data structures which contain the points to be plotted.
	"""
	# Arduino serial plotter has 500 points max. on the x axis.
	max_points = None  # maximum points per plot, put a limit to avoid storing / displaying too much data.
	tvec = []  # independent variable, with "max_points" points (the x in an xy plot)
	first = True  # first iteration only creating the plots

	dataset = None  		# complete dataset, this should go to a file. why should this go to a file !!!???
	np_dataset = None  		# used for reverting the matrix. (some math needs to be applied to map the data correctly)
	np_dataset_t = None		# transposed dataset, required to feed properly the plot. (is it really necessary) !!!???
	plot_refs = []  		# references to the different added plots.
	plot_subset = []		# From the data stored, only a subset is plotted. THIS IS THE ONLY DATA THAT IS PLOTTED IN THE END.
	enabled_graphs = []  	# enabled graphs ON GRAPH WINDOW, not on toggles.

	for i in range(0, MAX_PLOTS):
		enabled_graphs.append(False)	# list keeping track of which graphs are enabled.

	dataset_changed = False				# flag to keep track of changes on the dataset (graph only updates on changes)

	def __init__(self, dataset=None, max_points=500, title=""):
		"""
		Initializes the graph of the plot, setting background, range, limits and so on.
		:param dataset: 		Where the data of the graphs to be plotted will be stored.
		:param max_points:		Number of points per plotted graph, default 500.
		:param title:			Title of the plot.
		"""
		for i in range(max_points):  # create a time vector --> move to NUMPY !!!
			self.tvec.append(i)

		self.dataset = dataset  # get the reference to the dataset given as input for the constructor
		self.max_points = max_points

		# self.plot_subset = self.dataset[:self.n_plots][-(self.max_points):]	 # get only the portion of the dataset which needs to be printed.

		super().__init__()
		pg.setConfigOptions(antialias=False)  # antialiasing for nicer view.
		self.setBackground([70, 70, 70])  # changing default background color.
		# self.showGrid(x = True, y = True, alpha = 0.5)
		self.setRange(xRange=[0, self.max_points], yRange=[-10, 100])  # set default axes range
		self.setLimits(xMin=0, xMax=self.max_points, yMin=DEFAULT_Y_MIN,
		               yMax=DEFAULT_Y_MAX)  # THIS MAY ENTER IN CONFIG WITH PLOTTING !!!
		# self.enableAutoRange(axis='x', enable=True)																	# enabling autorange for x axis
		legend = self.addLegend()
		self.setTitle(title)  # if title is wanted

	def create_plots(self):
		"""
		Creates all plots (graphs) and adds a hook to manipulate them.
		The number of plots comes determined by the MAX_PLOTS constant.
		:return: None, only updates internal class variables.
		"""
		for i in range(MAX_PLOTS):
			logging.debug("val of i:" + str(i))
			p = self.plot(pen=(COLORS[i % 24]))
			self.plot_refs.append(p)

	def clear_plot(self):
		"""
		Clears all the plots (graphs).
		Used when neede to erase al graphs, for example when stop plot.
		:return: None
		"""
		print("clear_plot method called")
		for i in range(len(self.plot_subset)):
			self.plot_refs[i].clear()  # clears the plot
			# self.plot_refs[i].setData([0])  # sets the data to 0, may not be necessary

	def set_enabled_graphs(self, enable_list):  #
		"""
		Enabled/dsables graphs ON GRAPH WINDOW, not on the toggles.
		The graphs are enabled/disabled according to the enable_list, which updates based in the toggles.
		:param enable_list:	List with true/false values for each of the graphs. also "all" or "none" instead
		of a list can be used as enable_list values.
		:return:
		"""
		if enable_list == "all":
			enable_list = []
			for i in range(MAX_PLOTS):									# this refers to MAX_PLOTS, shouldn't it refer to n_plots???
				enable_list.append(True)
		elif enable_list == "none":
			enable_list = []
			for i in range(MAX_PLOTS):
				enable_list.append(False)
				print("enable_list all false")
		self.enabled_graphs = enable_list

	def update_graphs(self):
		"""
		This is the method that actually makes the repainting of the graphs
		In the first iteration, the graphs don't exist, so it creates them and
		from there takes the subset of data to be plotted (as the whole data stored is bigger than showed) and
		then assign the data to each channel.
		:return:
		"""
		# print("PLOT_TIMER MyGraph")
		# print (self.dataset_changed)

		if self.first == True:  # FIRST: CREATE THE PLOTS
			self.create_plots()
			print("len(self.plot_refs)")
			print(len(self.plot_refs))
			self.first = False
			print("First plot timer")

		# SECOND: UPDATE THE PLOTS:

		if (self.dataset_changed == True):  						# redraw only if there are changes on the dataset

			self.dataset_changed = False

			self.np_dataset = np.matrix(
				self.dataset[:][-self.max_points:])  				# we only use as subset the last max_points,
			self.np_dataset_t = self.np_dataset.transpose()  		# needed for correct dimensions
			self.plot_subset = self.np_dataset_t.tolist()  			# this is the data to be plotted, with a vector representing each variable

			# THIS IS ACTUALLY WHAT PLOTS THE DATA #
			for i in range(len(self.plot_subset)):
				if (self.enabled_graphs[i] == True):				# if graph is enabled, add the data to it.
					self.plot_refs[i].setData(
						self.plot_subset[i])  						# required for update: reassign references to the plots
				else:
					self.plot_refs[i].setData([])  					# if graph disabled (toggle not active) empty plot.

			pg.QtWidgets.QApplication.processEvents()				# for whatever reason, works faster when using processEvent.

class MyPlot(QWidget):
					
	n_plots = 6															# number of plots on the current plot.
	plot_tick_ms = 50													# every "plot_tick_ms", the plot updates, no matter if there's new data or not.
	dataset = []														# complete dataset, this should go to a file.							
	toggles = []														# references to the toggles which enable/disable plots.													
	
	def __init__(self, dataset = [], max_points = DEFAULT_MAX_POINTS):
		"""

		:param dataset: Datasheet to be plotted at the graph, could be given directly to graph instead.
		:param max_points: Maximum number of points to be plotted? or stored ???
		"""
		super().__init__()
		
		# central widget #
		self.layout = QHBoxLayout()										# that's how we will lay out the window
		self.setLayout(self.layout)
		self.graph = MyGraph(dataset = dataset, max_points = max_points)# this is the canvas object where the graphs are actually printed, this class is implemented on top of this code
		self.layout.addWidget(self.graph)
		self.layout_channel_select = QVBoxLayout()
		self.layout.addLayout(self.layout_channel_select)
		self.channel_label = QLabel("Channels:")
		self.layout_channel_select.addWidget(self.channel_label)
		self.add_toggles()												# add as many toggles as MAX_PLOTS, set them enabled but unchecked by default.
				
		self.layout_channel_name = QVBoxLayout()
		# timer #
		self.plot_timer = QTimer()										# used to update the plot
		self.plot_timer.timeout.connect(self.on_plot_timer)				# updates the plot in a regular basis
		self.start_plotting(self.plot_tick_ms)
		# self.stop_plotting()

		self.graph.set_enabled_graphs("none")							# writes to a variable of graph indicating which graphs are on
		
		print("Init until set_enabled_graphs")

		
		# ~ for toggle in self.toggles:
			# ~ print("IsChecked")
			# ~ print(toggle.isChecked())
			# ~ print("IsEnabled")
			# ~ print(toggle.isEnabled())
						
	def add_toggles(self):												# encapsulates the creation of the toggles, and their initial setup.
		for i in range(0, MAX_PLOTS):
			color = "#"+COLORS[i]										# !!! TAKE A LOOK TO THE #
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
		
	def set_channels_labels(self,names):
		"""
		Each channel toggle has a label, set the text on that label.
		:param names:
		Vector of names for the different channels, 
		can be maximum MAX_PLOTS size.
		:return: None
		"""
		for i in range(MAX_PLOTS):										# we only assign the names of the plots that can be plotted
			try:
				name = names[i][:CHANNEL_LABEL_MAX_LEN]
				self.toggles[i].setLabel(name)
			except Exception as e:
				logging.debug("more channels than labels")
				
	def clear_channels_labels(self):
		"""
		# clear all labels, usually to set them with new vals.
		:return: 
		"""
		for i in range(MAX_PLOTS):										# we only assign the names of the plots that can be plotted
			try:
				self.toggles[i].setLabel('')
			except Exception as e:
				logging.debug("more channels than labels")

	def set_max_points(self, max_points):
		"""
		The number of points to be plotted in the graphs is variable, with this function can be changed.
		Also adjusts the plot to the number of points.
		:param max_points: Set maximum number of points to be plotted, NOT RECOMMENDED > 5000 (makes plot heavy)
		:return:
		"""
		self.graph.max_points = max_points
		self.graph.setLimits(xMin=0, xMax=self.graph.max_points)
		self.graph.setXRange(0,self.graph.max_points)



	# def create_plots(self):
	# 	self.graph.create_plots()

	# def clear_plot(self):												# NOT WORKING
	# 	self.graph.clear_plot()


	def on_plot_timer(self):											# this is an option, to add together toggle processing and replot.
		"""
		There are two on_plot_timer functions, one for plot and one for graph
		do not confuse them.
		The one in plot, is an extension of the graph one.
		on_plot_timer performs two basic tasks:
		1. Update the active graphs based on the toggles (as the toggles belong to plot)
		2. Update the dataset 
		3. Execute graph's update_graph function, where the actual plotting of all graphs happens.
		:return: 
		"""
		enabled = []													# list containing true/false values for each graph
		for i in range(0,MAX_PLOTS):									# the list is of lenght MAX_PLOTS
			if(self.toggles[i].toggle.isChecked()):						# it updates its value with the toggle assigned to each of the graphs.
				enabled.append(True)
			else:
				enabled.append(False)		
			
		self.graph.set_enabled_graphs(enabled)							# update enabled grapgs
		
		self.graph.dataset = self.dataset								# update dataset MAY NOT BE BETTER TO DO THIS SOMEWHERE ELSE ???
						
		self.graph.update_graphs()										# calls the regular plot timer from graph.
		
	# def plot_timer_start(self):	# SEEMS UNUSED AND UNNECESSARY !!!
	# 	self.graph.timer.start()

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


## THIS PART WON'T BE EXECUTED WHEN IMPORTED AS A SUBMODULE, BUT ONLY WHEN TESTED INDEPENDENTLY ##

if __name__ == "__main__":

	class MainWindow(QMainWindow):

		n_plots = 6
		# class variables #
		data_tick_ms = 10

		#creating a fixed size dataset #
		dataset = []
	
		# constructor # 
		def __init__(self):
			
			super().__init__()

			# add graph and show #
			#self.graph = MyGraph(dataset = self.dataset)
			self.plot = MyPlot(dataset = self.dataset)					# extend the constructor, to force giving a reference to a dataset ???
			# self.plot.graph.set_enabled_graphs("none")
			# self.plot.set
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

			# instead of using a timer to get the data,
			# use a signal from terminal_widget that triggers the collecting of the data.
			# self.data_timer = QTimer()
			# self.data_timer.timeout.connect(self.on_data_timer)
			# self.data_timer.start(self.data_tick_ms)

			self.plot.check_toggles("none")								# by default all toggles are on, making all graphs active.
			self.plot.enable_toggles("all")								# enables the toggles which control the graphs, so they can be enabled and disabled from the toggle.
								


			self.setCentralWidget(self.plot)
			# last step is showing the window #
			self.show()
			
			#self.plot.graph.plot_timer.start()

		# unneeded with new approach #
		# def on_data_timer(self):										# simulate data coming from external source at regular rate.
		# 	t0 = time.time()
		# 	logging.debug("length of dataset: " + str(len(self.plot.dataset)))
		#
		#
		# 	line = []
		# 	for i in range(0,self.n_plots):
		# 			line.append(random.randrange(0,100))
		# 			self.dataset.append(line)
		# 			# line.append(random.randrange(0, 80))
		# 			# self.dataset.append(line)
		# 			# line.append(random.randrange(0, 120))
		# 			# self.dataset.append(line)
		#
		# 	# print("self.dataset")
		# 	# for data in self.dataset:
		# 	# 	print(data)
		#
		# 	self.plot.dataset = self.dataset							# this SHOULD HAPPEN INTERNAL TO THE CLASS !!!
		#
		# 	self.plot.update()
		# 	t = time.time()
		# 	dt = t - t0
		# 	logging.debug("execution time add_stuff_dataset " + str(dt))
			

	app = QApplication([])
	app.setStyle("Fusion")												# required to use it here
	mw = MainWindow()
	app.exec_()

