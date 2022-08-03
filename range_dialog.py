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
	QDialogButtonBox,
	QFormLayout,
)

from PyQt5.QtCore import (
	QTimer,
	Qt,
	pyqtSignal,
)

from PyQt5.QtGui import (
	QIntValidator,
)

COLORS = ["ff0000", "00ff00", "0000ff", "ffff00", "ff00ff", "00ffff",
		  "ff0000", "00ff00", "0000ff", "ffff00", "ff00ff", "00ffff",
		  "ff0000", "00ff00", "0000ff", "ffff00", "ff00ff", "00ffff",
		  "ff0000", "00ff00", "0000ff", "ffff00", "ff00ff", "00ffff",

		  ]

MAX_PLOTS = 24  # Absolute maximum number of plots, change if needed !!
ABS_MAX_RANGE = 1000000


class RangeDialog(QDialog):
	def __init__(self, absolute_max_range = None):
		super().__init__()

		self.min_textbox = QLineEdit(self)
		self.max_textbox = QLineEdit(self)
		self.onlyInt = QIntValidator()
		self.min_textbox.setValidator(self.onlyInt)
		self.max_textbox.setValidator(self.onlyInt)
		buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

		layout = QFormLayout(self)
		layout.addRow("Minimum", self.min_textbox)
		layout.addRow("Maximum", self.max_textbox)
		layout.addWidget(buttonBox)

		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

	def getInputs(self):
		return (self.min_textbox.text(), self.max_textbox.text())


class RangeDialogOldOld(QDialog):  # this is supposed to be the python convention for classes.

	# variables #
	max = None				# parameters to be returned
	min = None
	# signals #
	range = pyqtSignal(int, int)					# This signal will be used to send the range chosen in the popup window.
	okPressed = pyqtSignal()
	cancelPressed = pyqtSignal()


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

	def accept(self):			#
		pass

	def closeEvent(self, event):
		print("CLOSING AND CLEANING UP:")
		self.shortcuts_table = None
		super().close()
# event.ignore()

class RangeDialogOld(QDialog):

	min_val = None
	max_val = None

	def __init__(self, parent=None):

		super().__init__(parent)

		self.setWindowTitle("Set range")
		# main layout #
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
		# add buttons to the button box (inherited from QDialog)
		QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		self.layout.addWidget(self.buttonBox)

		#
		self.setModal(True)							# should be by default, but didn't seem to work
		#
		# self.show()

	def accept(self):
		self.min_val = self.textbox_min.text()
		self.max_val = self.textbox_max.text()

		# print("The minimum value")
		# print(self.min_val)
		#return(self.min_val)
		self.close()
		print("reacher end of accept")

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
		#self.setWindowModality(Qt.ApplicationModal)				# other windows are blocked until this window is closed
		self.show()  # window is created and destroyed every time we change the values

	def on_click_range_button(self):  		#
		self.range_setter = RangeDialog(ABS_MAX_RANGE)  	# needs to be self, or it won't persist
		if self.range_setter.exec():
			print(self.range_setter.getInputs())

		for inp in self.range_setter.getInputs():
			print(inp)

## THIS PART WON'T BE EXECUTED WHEN IMPORTED AS A SUBMODULE, BUT ONLY WHEN TESTED INDEPENDENTLY ##

if __name__ == "__main__":

	app = QApplication([])
	app.setStyle("Fusion")  # required to use it here
	mw = MainWindow()
	app.exec_()


