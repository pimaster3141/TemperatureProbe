from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time

class Plotter():

	def __init__(windowSize, dataReader, logger, dataRate = -1):
		self.windowSize = windowSize
		self.data1 = {} # time :  data

		self.win = pg.GraphicsWindow()
		self.win.setWindowTitle('Data Window')

		self.p1 = self.win.addPlot(title = "Channel 1")
		self.p1.setLabel('bottom', 'Time', 's')
		self.p1.setLabel('left', 'LSB')

		self.dataReader = DataReader.Reader()

		self.data1[0] = [self.dataReader.read(1)]
		self.startTime = time.perf_counter()
		self.lastTime = self.startTime

		self.curve1 = self.p1.plot(x=list(self.data1.keys()), y=list(self.data1.values()))

	def updateData(size):
		rawData = self.dataReader.read(size)

		readTime = time.perf_counter()
		elapsedTime = readTime - lastTime
		xVals = np.linspace(self.lastTime, self.readTime, len(data))

		data = dict(zip(xVals, rawData))
		return data

	def update():
		

