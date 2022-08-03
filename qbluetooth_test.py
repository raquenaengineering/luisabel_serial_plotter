#!/usr/bin/env python
import signal
import sys
import os

from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtBluetooth import QBluetoothLocalDevice, QBluetoothDeviceDiscoveryAgent, QBluetoothDeviceInfo


class Application(QCoreApplication):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.dev = QBluetoothDeviceInfo()
		self.dlist = []
		self.counter = 0

		self.localDevice = QBluetoothLocalDevice()
		print(self.localDevice.name())

		self.scan_for_devices()
		self.exec()

	def display_status(self):
		d = 0

	# print(self.agent.isActive(), self.agent.discoveredDevices())

	def fin(self, *args, **kwargs):
		self.agent.stop()
		self.dlist = self.agent.discoveredDevices()
		while self.counter < len(self.dlist):
			print(self.dlist[self.counter].name())
			self.counter += 1
		os.environ['QT_EVENT_DISPATCHER_CORE_FOUNDATION'] = '0'
		sys.exit(0)

	def err(self, *args, **kwargs):
		print("Ein Fehler ist aufgetretten.")

	def scan_for_devices(self):
		self.agent = QBluetoothDeviceDiscoveryAgent(self)
		# self.agent.deviceDiscovered.connect(self.fin)
		self.agent.finished.connect(self.fin)
		self.agent.error.connect(self.err)
		self.agent.setLowEnergyDiscoveryTimeout(10000)
		# self.agent.discoveredDevices()

		self.agent.start()

		timer = QTimer(self.agent)
		timer.start(500)
		timer.timeout.connect(self.display_status)


if __name__ == '__main__':
	import sys

	os.environ['QT_EVENT_DISPATCHER_CORE_FOUNDATION'] = '1'

	app = Application(sys.argv)

