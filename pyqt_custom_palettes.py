
import sys


from PyQt5.QtCore import(
	Qt
)

from PyQt5.QtGui import(
	QPalette,
	QColor	
)

from PyQt5.QtWidgets import(
	QMainWindow,
	QApplication,
	QLabel
)


class dark_palette(QPalette):
	def __init__(self):
		super().__init__()

		self.setColor(QPalette.Window, QColor(53, 53, 53)) 
		self.setColor(QPalette.WindowText, Qt.white) 
		self.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127)) 
		self.setColor(QPalette.Base, QColor(42, 42, 42)) 
		self.setColor(QPalette.AlternateBase, QColor(66, 66, 66)) 
		self.setColor(QPalette.ToolTipBase, Qt.white) 
		self.setColor(QPalette.ToolTipText, Qt.white) 
		self.setColor(QPalette.Text, Qt.white) 
		self.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127)) 
		self.setColor(QPalette.Dark, QColor(35, 35, 35)) 
		self.setColor(QPalette.Shadow, QColor(20, 20, 20)) 
		self.setColor(QPalette.Button, QColor(53, 53, 53)) 
		self.setColor(QPalette.ButtonText, Qt.white) 
		self.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127)) 
		self.setColor(QPalette.BrightText, Qt.red) 
		self.setColor(QPalette.Link, QColor(42, 130, 218)) 
		self.setColor(QPalette.Highlight, QColor(42, 130, 218)) 
		self.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80)) 
		self.setColor(QPalette.HighlightedText, Qt.white) 
		self.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127)) 


class light_palette(QPalette):

	def __init__(self):
		super().__init__()
	
		# changing all color palette parameters inside the class #
		self.setColor(QPalette.Window, QColor(250,250,250))								# quite clear grey
		self.setColor(QPalette.WindowText, QColor(42,42,42))							# window text			(255,150,100) also looks good
		self.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127,127,127))		# what does this do ???
		self.setColor(QPalette.Button, QColor(200,200,200))								# not working !!!
		self.setColor(QPalette.ButtonText, Qt.black)									# works fine

		self.setColor(QPalette.Base, QColor(200,200,200))									# base color =???
		self.setColor(QPalette.AlternateBase, QColor(42,42,42))						
		self.setColor(QPalette.ToolTipBase, QColor(42,42,42))						
		self.setColor(QPalette.ToolTipText, Qt.white)
		self.setColor(QPalette.Text, Qt.white)											# why white ??
		self.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
		self.setColor(QPalette.Dark, QColor(35, 35, 35))



class custom_palette(QPalette):
	def __init__(self):
		super().__init__()

		# changing all color palette parameters inside the class #
		self.setColor(QPalette.Window, QColor(53,53,53))						# window color
		self.setColor(QPalette.WindowText, Qt.white)							# window text
		self.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127,127,127))	# what does this do ???

		self.setColor(QPalette.Base, QColor(42,42,42))						# base color =???
		# ~ darkPalette.setColor(QPalette.AlternateBase, QColor(42,42,42))						
		# ~ darkPalette.setColor(QPalette.ToolTipBase, QColor(42,42,42))						
		# ~ darkPalette.setColor(QPalette.ToolTipText, Qt.white)
		# ~ darkPalette.setColor(QPalette.Text, Qt.white)
		# ~ darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
		# ~ darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
		
		# add custom color for the pyqtgrap
		

class re_palette(QPalette):														# palette for Raquena Engineering Apps
	def __init__(self):
		super().__init__()

		# changing all color palette parameters inside the class #
		self.setColor(QPalette.Window, QColor(250,250,250))						# quite clear grey
		self.setColor(QPalette.WindowText, QColor(255,150,150))				# window text			(255,150,100) also looks good
		self.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127,127,127))	# what does this do ???
		self.setColor(QPalette.Button, Qt.black)								# not working !!!
		self.setColor(QPalette.ButtonText, Qt.red)								# works fine

		self.setColor(QPalette.Base, QColor(42,42,42))						# base color =???
		self.setColor(QPalette.AlternateBase, QColor(42,42,42))						
		self.setColor(QPalette.ToolTipBase, QColor(42,42,42))						
		self.setColor(QPalette.ToolTipText, Qt.white)
		self.setColor(QPalette.Text, Qt.white)
		self.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
		self.setColor(QPalette.Dark, QColor(35, 35, 35))





