
import random
import time 
import logging

import numpy as np

import csv


from PyQt5.QtWidgets import(
	QApplication,
	QMainWindow,
	QWidget,
	QVBoxLayout,
	QListWidget,
	QPushButton,
	QHBoxLayout,
	QTableView,
	QTableWidget,
	QTableWidgetItem,
	QAbstractItemView,
	QAbstractScrollArea,

)

from PyQt5.QtCore import(
	QTimer,
	Qt,
)
import pyqtgraph as pg


COLORS = ["ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",
			"ff0000","00ff00","0000ff","ffff00","ff00ff","00ffff",

]

MAX_PLOTS = 24															# Absolute maximum number of plots, change if needed !!


class ShortcutsWidget(QWidget):											# this is supposed to be the python convention for classes. 
	
	
	shortcuts = [[],[]]
	actions = shortcuts[0]												# list of the actions			
	keys = shortcuts[1]													# keys associated with the actions
	
	def __init__(self):
		
		super().__init__()	
		self.setWindowTitle("Shortcuts")
		self.resize(800,600)											# setting initial window size
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)	
		# list # (remove when table well implemented)
		self.shortcuts_list = QListWidget()								# maybe move to a table (fixed left, editable right)
		#self.layout.addWidget(self.shortcuts_list)
		# table#
		self.shortcuts_table = QTableWidget()
		self.layout.addWidget(self.shortcuts_table)
		self.shortcuts_table.setShowGrid(False)
		self.shortcuts_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.shortcuts_table.verticalHeader().setVisible(False);
		self.shortcuts_table.setSizeAdjustPolicy(
        QAbstractScrollArea.AdjustToContents)
		header = self.shortcuts_table.horizontalHeader()
		self.shortcuts_table.resizeColumnsToContents()
		#header.setFrameStyle(QFrame.Box | QFrame.Plain)
		self.shortcuts_table.horizontalHeader().setVisible(True);
		header.setLineWidth(1)
		self.shortcuts_table.setHorizontalHeader(header)
		self.shortcuts_table.setSizeAdjustPolicy(
        QAbstractScrollArea.AdjustToContents)
		
		# filling table #
		self.load_shortcuts()
		self.fill_shortcuts_table()

		# buttons #
		self.buttons_layout = QHBoxLayout()
		self.layout.addLayout(self.buttons_layout)
		self.load_button = QPushButton("Load")
		self.buttons_layout.addWidget(self.load_button)
		self.load_button.clicked.connect(self.load_shortcuts)
		self.save_button = QPushButton("Save")
		self.buttons_layout.addWidget(self.save_button)	
		self.save_button.clicked.connect(self.save_shortcuts)			
		self.default_button = QPushButton("Default")
		self.buttons_layout.addWidget(self.default_button)
		self.default_button.clicked.connect(self.default_shortcuts)		
	
		self.setWindowModality(Qt.ApplicationModal)
		self.show()														# window is created and destroyed every time we change shortcuts.
		
		
		# DISABLE STUFF WHICH CAN'T BE USED YET ########################
		self.load_button.setEnabled(False)
		self.save_button.setEnabled(False)
		self.default_button.setEnabled(False)		
		################################################################

	def load_shortcuts(self):
		print("load_shortcuts method called:")
		# ~ # should open a popup window to select the file #
		with open("resources/shortcuts.txt") as sc_file:
			csv_reader = csv.reader(sc_file,delimiter = ',')
			for row in csv_reader:
				self.actions.append(row[0])								# is this the use of a dictiorary?
				self.keys.append(row[1])
				
			print("Shortcuts")
			for shortcut in self.shortcuts:
				print(shortcut)
			# ~ vals = sc_file.read().splitlines()
			# ~ print(vals)
			# ~ #vals = vals.splitlines()
			# ~ for line in vals:
				# ~ self.shortcuts.append(line)
			# ~ #print(self.shortcuts)
	


	def save_shortcuts(self):											# NOT WORKING 
		print("save_shortcuts method called:")


	def default_shortcuts(self):										# NOT WORKING 
		print("default_shortcuts method called:")
		# how to set the defaults ??
		# 1. hard coded onto the main window.
			# advantages: no way the user can screw it up, disadvantages: code dirtier, difficult to maintain?
		# 2. readed from configuration file which is also python-like interpretable. 
			# advantages: is already code, disadvantages: not standard.
		# 3. readed from a configuration file with exactly the same format as the used shortcuts file
			
			
	def fill_shortcuts_table(self):
		# for now use internal shortcuts, maybe better to give the shortcuts table as an input parameter. 
		#self.shortcuts_table.setModel(self.shortcuts)
		self.shortcuts_table.setRowCount(len(self.shortcuts[0]))
		self.shortcuts_table.setColumnCount(2)
		# ~ for i in range(0,len(self.shortcuts[0])):
			# ~ self.shortcuts_table.setItem(i,0,QTableWidgetItem(self.shortcuts[i]))
		for i in range(len(self.actions)):
			self.shortcuts_table.setItem(i,0,QTableWidgetItem(self.actions[i]))
		for i in range(len(self.keys)):
			self.shortcuts_table.setItem(i,1,QTableWidgetItem(self.keys[i]))

		self.shortcuts_table.setHorizontalHeaderLabels(["Action","Shortcut"])
		self.shortcuts_table.resizeColumnsToContents()
		# ~ self.shortcuts_table.setFixedWidth(							# this resizes the table, but not the window where the table is...
			# ~ self.shortcuts_table.columnWidth(0) + 
			# ~ self.shortcuts_table.columnWidth(1)
			# ~ )
		

		
	def closeEvent(self, event):
		print("CLOSING AND CLEANING UP:")
		self.shortcuts_table = None
		super().close()
		#event.ignore()	

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


