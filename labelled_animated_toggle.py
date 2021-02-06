
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
	def getLabel(self):
		label = self.label.text()
		return(label)
		
	def setChecked(self, val):
		self.toggle.setChecked(val)
	def isChecked(self):
		return(self.toggle.isChecked())
		
	def setEnabled(self, val):
		self.toggle.setEnabled(val)
	def isEnabled(self):
		return(self.toggle.isEnabled())
