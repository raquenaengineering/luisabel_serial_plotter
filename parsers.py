

"""
Function to convert arduino data into values
"""

START_OF_TEXT = '"'
END_OF_TEXT = '#'


arduino_test_text: str = '1,3,24,12,2;"caption 1, caption 2, cara de pene, aaa# 10,10,20,250,111; 100,100,3;'

def arduino_parser(readed):											# perform data processing as required (START WITH ARDUINO STYLE, AND ADD OTHER STYLES).#

	vals = readed.replace(' ' ,',')									# replace empty spaces for commas.
	vals = vals.replace(':' ,',')									# fast fix for inline labels incompatibility. MAKE IT BETTER !!!
	vals = vals.split(',')											# arduino serial plotter splits with both characters.

	valsf = []
	captions = []

	# self.plot_frame.n_plots = 5										# !!! NOT FOR PARSING !!!


	# ADD CASE SOMEWHERE TO CONSIDER SPECIAL CHARACTERS FOR THE PARSING !!!
	# for example as we use ascii, and we want to send numbers,
	# 1. all non-numerical characters can be considered caption
	# 2. Or use special characters (from 251 to 255 for example)

	if(vals[0] == ''):												# this case may not be needed anymore
		# self.timeouts = self.timeouts + 1
		print("Timeout")
		# print("Total number of timeouts:  "+ str(self.timeouts))	# !!! probably trying to fix something else not belonging to parsing.
	else:
		# for val in vals:
		# 	try:
		# 		valsf.append(float(val))
		# 	except:
		# 		logging.debug("It contains also text");
		# 		# add to a captions vector
		# 		text_vals = vals
		# 		self.plot_frame.set_channels_labels(text_vals)		# this sets all labels, I need to set them independently !!!
		# 	else:
		# 		self.add_values_to_dataset(valsf)
		text_vals = []
		for val in vals:
			try:
				valsf.append(float(val))
			except:
				# logging.debug("It contains also text")
				# add to a captions vector
				text_vals.append(val)
				# self.plot_frame.set_channels_labels(text_vals)	# !!! NOTHING TO DO WITH PARSING
			else:
				self.add_values_to_dataset(valsf)					# !!! NOTHING TO DO WITH PARSING

		self.plot_frame.update()
	# print("dataset_changed = "+ str(self.plot_frame.graph.dataset_changed))

	return(valsf, captions)

	def emg_parse(self):
		pass

	def add_emg_sensor_data(self):								# reads the data in the specific binary format of the emg sensor

		byte_buffer = []
		num_buffer = []

		try:
			byte_buffer = self.serial_port.read(SERIAL_BUFFER_SIZE)		# up to 1000 or as much as in buffer.
		except Exception as e:
			self.on_port_error(e)
			self.on_button_disconnect_click()							# we've crashed the serial, so disconnect and REFRESH PORTS!!!
		else:															# if except doens't happen
			# print("byte_buffer:")
			# print(byte_buffer)

			try:
				for byte in byte_buffer:
					num = int(byte)
					num_buffer.append(num)
					# print("num_buffer:")
					# print(num_buffer)
				# here we will have a buffer with lots of numbers (32,45,33,0,45,54,33,0,32...)
			except Exception as e:
				print("ERROR: -------------------------")
				print(e)
				print(SEPARATOR)
				self.on_port_error(e)
			else:
				self.read_buffer = self.read_buffer + num_buffer			# read buffer contains what was left from previous iteration
				data_points = self.split_number_array(self.read_buffer,0)	# we split the buffer on 'number 0' received (end of data_points)
				self.read_buffer = data_points[-1]  						# clean the buffer, saving the non completed data_points
				a = data_points[:-1]										# get all the completed ones
				for data_point in a:  										# so all data points except last.
					if len(data_point) == 4:								# FIX THIS!: we expect 4 data values per data point, if not, it means corrupted data.
						self.add_values_to_dataset(data_point)

				# HERE IS WHERE WE GET THE PROBLEMATIC DATA POINTS, SO THE RIGHT PLACE TO FIX IF THERE AREN'T ENOUGH POINTS.
					else:
						for i in range(int(len(data_point)/4)+1):
							self.add_values_to_dataset([0,0,0,0])				# this indicates error code, data isn't having the 4 expected values




				pass
		self.plot_frame.update()
		# num = True
		# vals = []
		# while(num != 0):
		# 	byte = self.serial_port.read()
		# 	num = int.from_bytes(byte, byteorder='big', signed=False)  # decoding to store in file
		# 	num = float(num)
		# 	vals.append(num)
		# vals = vals[:-1]										# remove the final zero
		# if(len(vals) > 1):										# bad trick to remove zero data value array !!!
		# 	self.add_values_to_dataset(vals)
		# 	self.plot_frame.update()
		# 	#return(vals)
	def add_emg_new_sensor_data(self):								# reads the data in the specific binary format of the emg sensor
		#print("add_emg_new_sensor_data")
		byte_buffer = []
		num_buffer = []

		try:
			byte_buffer = self.serial_port.read(SERIAL_BUFFER_SIZE)		# up to 1000 or as much as in buffer.
		except Exception as e:
			self.on_port_error(e)
			self.on_button_disconnect_click()							# we've crashed the serial, so disconnect and REFRESH PORTS!!!
		else:															# if except doens't happen
			# print("byte_buffer:")
			# print(byte_buffer)

			try:
				for byte in byte_buffer:
					num = int(byte)
					num_buffer.append(num)
				# print("num_buffer:")
				# print(num_buffer)
				# here we will have a buffer with lots of numbers (32,45,33,0,45,54,33,0,32...)
			except Exception as e:
				print("ERROR: -------------------------")
				print(e)
				print(SEPARATOR)
				self.on_port_error(e)
			else:
				self.read_buffer = self.read_buffer + num_buffer				# read buffer contains what was left from previous iteration
				data_points = self.split_number_array(self.read_buffer,0xFF)	# we split the buffer on 'number FF' received (end of data_points)
				self.read_buffer = data_points[-1]  							# clean the buffer, saving the non completed data_points
				a = data_points[:-1]											# get all the completed ones
				for data_point in a:  											# so all data points except last.
					if len(data_point) == 4:									# FIX THIS!: we expect 4 data values per data point, if not, it means corrupted data.
						self.add_values_to_dataset(data_point)
						pass
				# HERE IS WHERE WE GET THE PROBLEMATIC DATA POINTS, SO THE RIGHT PLACE TO FIX IF THERE AREN'T ENOUGH POINTS.
					else:
						for i in range(int(len(data_point)/4)+1):
							self.add_values_to_dataset([0,0,0,0])				# this indicates error code, data isn't having the 4 expected values

		self.plot_frame.update()

if __name__ == "__main__":
	values,captions = arduino_parser(arduino_test_text)