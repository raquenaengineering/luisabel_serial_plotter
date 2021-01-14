
import random
import time 
import logging

import numpy as np


from PyQt5.QtWidgets import(
	QApplication,
	QMainWindow,
	QWidget,
	QVBoxLayout,
	QListWidget,
	QPushButton,
	QHBoxLayout,

)

from PyQt5.QtCore import(
	QTimer,
	Qt
)
import pyqtgraph as pg


COLORS = ["ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",

]

MAX_PLOTS = 24															# Absolute maximum number of plots, change if needed !!


class ShortcutsWidget(QWidget):												# this is supposed to be the python convention for classes. 
	
	# Arduino serial plotter has 500 points max. on the x axis.
	max_points = None													# maximum points per plot
	
	shortcuts = []

	
	def __init__(self):
		
		super().__init__()	
		self.setWindowTitle("Shortcuts")
		self.resize(800,600)										# setting initial window size
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)	
		self.shortcuts_list = QListWidget()								# maybe move to a table (fixed left, editable right)
		self.layout.addWidget(self.shortcuts_list)
		self.buttons_layout = QHBoxLayout()
		self.layout.addLayout(self.buttons_layout)
		self.load_button = QPushButton("Load")
		self.buttons_layout.addWidget(self.load_button)
		self.load_button.clicked.connect(self.load_shortcuts)
		self.save_button = QPushButton("Save")
		self.buttons_layout.addWidget(self.save_button)	
		self.save_button.clicked.connect(self.save_shortcuts)			
		self.load_button = QPushButton("Default")
		self.buttons_layout.addWidget(self.load_button)
		self.load_button.clicked.connect(self.default_shortcuts)		
		
		
		self.setWindowModality(Qt.ApplicationModal)
		self.show()														# window is created and destroyed every time we change shortcuts.

	def load_shortcuts(self):
		print("load_shortcuts method called:")
		self.shortcuts_list.clear()										# start from clean table every time.
		with open("shortcuts.txt") as sc_file:
			vals = sc_file.readlines()
			print(vals)
			#vals = vals.splitlines()
			self.shortcuts_list.addItems(vals)
			for i in range(0,20):
				self.shortcuts_list.addItems([["21","22","23"],["21","21","21"]])

	def save_shortcuts(self):											# NOT WORKING 
		print("save_shortcuts method called:")


	def default_shortcuts(self):											# NOT WORKING 
		print("default_shortcuts method called:")


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

			self.setWindowTitle("Testing shorcuts menu window")
			# create shortcuts widget to test the class #
			self.shortcuts_button = QPushButton("Shortcuts")
			self.shortcuts_button.clicked.connect(self.on_click_shortcuts_button)
			self.resize(1200,800)										# setting initial window size
			self.setCentralWidget(self.shortcuts_button) 
			# last step is showing the window #
			self.show()

		def on_click_shortcuts_button(self):							# simulate data coming from external source at regular rate.
				self.shortcuts = ShortcutsWidget()							# needs to be self, or it won't persist
			

	app = QApplication([])
	app.setStyle("Fusion")												# required to use it here
	mw = MainWindow()
	app.exec_()


