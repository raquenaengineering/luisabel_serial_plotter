import random
import time
import logging

import numpy as np

import csv

from PyQt5.QtWidgets import (
	QApplication,
	QMainWindow,
	QWidget,
	QVBoxLayout,
	QPushButton,
	QHBoxLayout,
	QTableWidgetItem,
	QLineEdit,
	QLabel,
	QDialog,
)

from PyQt5.QtCore import (
	QTimer,
	Qt,
)

COLORS = ["ff0000", "00ff00", "0000ff", "ffff00", "ff00ff", "00ffff",
		  "ff0000", "00ff00", "0000ff", "ffff00", "ff00ff", "00ffff",
		  "ff0000", "00ff00", "0000ff", "ffff00", "ff00ff", "00ffff",
		  "ff0000", "00ff00", "0000ff", "ffff00", "ff00ff", "00ffff",

		  ]

MAX_PLOTS = 24  # Absolute maximum number of plots, change if needed !!


class RangeDialog(QDialog):  # this is supposed to be the python convention for classes.

	max = None				# parameters to be returned
	min = None

	def __init__(self):

		super().__init__()
		self.setWindowTitle("Set Range")
		self.resize(400, 200)  # setting initial window size
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		# text boxes #
		self.textboxes_layout = QHBoxLayout()
		self.textbox_min = QLineEdit()
		self.textboxes_layout.addWidget(self.textbox_min)
		self.separator = QLabel("--")
		self.textboxes_layout.addWidget(self.separator)
		self.textbox_max = QLineEdit()
		self.textboxes_layout.addWidget(self.textbox_max)
		self.layout.addLayout(self.textboxes_layout)
		# buttons #
		self.buttons_layout = QHBoxLayout()
		self.layout.addLayout(self.buttons_layout)
		self.cancel_button = QPushButton("Cancel")
		self.buttons_layout.addWidget(self.cancel_button)
		self.cancel_button.clicked.connect(self.on_cancel)
		self.ok_button = QPushButton("Ok")
		self.buttons_layout.addWidget(self.ok_button)
		self.ok_button.clicked.connect(self.on_ok)

		self.setWindowModality(Qt.ApplicationModal)
		self.show()  # window is created and destroyed every time we change shortcuts.

		# DISABLE STUFF WHICH CAN'T BE USED YET ########################

	################################################################

	def on_ok(self):
		# use return values to spit back new range
		# alternatively, create a signal, for the parent window to subscribe, so I can save the data coming from this #
		# alternatively, this data can be stored in a configuration file, which should be reviewed after every change in config #
		pass
		return(self.max, self.min)
		self.close()

	def on_cancel(self):  # NOT WORKING
		self.close()


	def closeEvent(self, event):
		print("CLOSING AND CLEANING UP:")
		self.shortcuts_table = None
		super().close()
# event.ignore()


## THIS PART WON'T BE EXECUTED WHEN IMPORTED AS A SUBMODULE, BUT ONLY WHEN TESTED INDEPENDENTLY ##

if __name__ == "__main__":
	class MainWindow(QMainWindow):
		# class variables #
		data_tick_ms = 5

		# creating a fixed size dataset #
		dataset = []

		# constructor #
		def __init__(self):
			super().__init__()

			self.setWindowTitle("Testing shorcuts menu window")
			# create shortcuts widget to test the class #
			self.set_range_button = QPushButton("Set Range")
			self.set_range_button.clicked.connect(self.on_click_range_button)
			self.resize(1200, 800)  # setting initial window size
			self.setCentralWidget(self.set_range_button)
			# last step is showing the window #
			self.show()

		def on_click_range_button(self):  # simulate data coming from external source at regular rate.
			range = self.range_setter = RangeDialog()  # needs to be self, or it won't persist
			print("This is the new range")
			print(range)


	app = QApplication([])
	app.setStyle("Fusion")  # required to use it here
	mw = MainWindow()
	app.exec_()


