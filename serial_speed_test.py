
# SERIAL_SPEED_TEST:

# this script will be used to calculate the maximum throughput of the different modalities of serial ports:#
# SIL2104 	(ESP32 SERIAL TO USB CONVERTER)
# BLUETOOTH	(ESP32)
# NATIVE USB(TEENSY)


# standard imports #
import sys											# deal with OS, open files and so
import time 										# delays, and time measurement ?
import random										# random numbers
import os											# dealing with directories

import serial										# required to handle serial communication
import serial.tools.list_ports						# to list already existing ports

import csv
import numpy as np 									# required to handle multidimensional arrays/matrices

import logging
#logging.basicConfig(level=logging.DEBUG)			# enable debug messages
logging.basicConfig(level = logging.WARNING)


class serial_speed_tester():

	serial_port = None

	def __init__(self):
		pass

	def serial_connect(self, port_name):
		logging.debug("serial_connect method called")
		logging.debug(port_name)
		logging.debug("port name " + port_name)

		try:  # closing port just in case was already open. (SHOULDN'T BE !!!)
			self.serial_port.close()
			logging.debug("Serial port closed")
			logging.debug(
				"IT SHOULD HAVE BEEN ALWAYS CLOSED, REVIEW CODE!!!")  # even though the port can't be closed, this message is shown. why ???
		except:
			logging.debug("serial port couldn't be closed")
			logging.debug("Wasn't open, as it should always be")

		try:  # try to establish serial connection
			self.serial_port = serial.Serial(  # serial constructor
				port=port_name,
				baudrate=self.serial_baudrate,
				# baudrate = 115200,
				# bytesize=EIGHTBITS,
				# parity=PARITY_NONE,
				# stopbits=STOPBITS_ONE,
				# timeout=None,
				timeout=0,  # whenever there's no dat on the buffer, returns inmediately (spits '\0')
				xonxoff=False,
				rtscts=False,
				write_timeout=None,
				dsrdtr=False,
				inter_byte_timeout=None,
				exclusive=None
			)

		except Exception as e:  # both port open, and somebody else blocking the port are IO errors.
			logging.debug("ERROR OPENING SERIAL PORT")
			#self.on_port_error(e)

		except:
			logging.debug("UNKNOWN ERROR OPENING SERIAL PORT")

		else:  # IN CASE THERE'S NO EXCEPTION (I HOPE)
			logging.debug("SERIAL CONNECTION SUCCESFUL !")
			self.status_bar.showMessage("Connected")
		# here we should also add going  to the "DISCONNECT" state.

		logging.debug("serial_port.is_open:")
		logging.debug(self.serial_port.is_open)
		logging.debug("done: ")


# logging.debug(self.done)


if __name__ == '__main__':
	# tester = serial_speed_tester()
	# tester.serial_connect("COM17")

	repetitions = 20
	time_span = 1
	n_vals_tot = 0

	#serial_port = serial.Serial("COM17")
	serial_port = serial.Serial("COM4")


	i = 0
	while (i < repetitions):
		t = time.time()
		t0 = time.time()
		dt = 0
		while (dt <= time_span):
			vals = serial_port.read(100);
			n_vals = len(vals)
			n_vals_tot = n_vals_tot + n_vals
			#print(vals);
			t = time.time()
			dt = t - t0
		print(dt)
		print(n_vals_tot)
		n_vals_tot = 0
		i = i + 1
	serial_port.close()
