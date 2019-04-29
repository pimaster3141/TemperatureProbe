import PyQt5
import pyqtgraph as pg
import numpy as np
import time
import queue

class GraphWindow():
	QUEUE_TIMEOUT = 5;

	def __init__(self, dataBuffer, sampleRate, depth=10, refreshRate=30, stopFcn=None):
		self.dataBuffer = dataBuffer;
		self.depth = depth;
		self.sampleRate = sampleRate;
		self.refreshRate = refreshRate;
		self._refreshPeriod = 1/self.refreshRate;

		self.numSamples = int(self.depth * self.sampleRate);
		self.xData = np.arange(-self.numSamples, 0)/self.sampleRate;

		self.stopFcn = stopFcn;

		self.isAlive = True;
		self._lastTime = time.time();

		self.setupPlots();
		self.setupDataBuffers();
		self.setupCurves();

	def setupPlots(self):
		self.win = pg.GraphicsWindow("Temperature");
		self.win.closeEvent = self.closeEvent;

		self.refPlot = self.win.addPlot(title="Reference Probe", labels={'left':('Temp', 'C'), 'bottom':('Time', 's')}, row=0, col=0);
		self.refPlot.setMouseEnabled(x=False, y=False);
		self.refPlot.enableAutoRange(x=True, y=True);
		self.refPlot.showGrid(x=True, y=True);

		self.tempPlot = self.win.addPlot(title="Temperature Probe", labels={'left':('Temp', 'C'), 'bottom':('Time', 's')}, row=1, col=0);
		self.tempPlot.setMouseEnabled(x=False, y=False);
		self.tempPlot.enableAutoRange(x=True, y=True);
		self.tempPlot.showGrid(x=True, y=True);

		self.vapPlot = self.win.addPlot(title="Vaporizer", labels={'bottom':('Time', 's')}, row=2, col=0);
		self.vapPlot.setMouseEnabled(x=False, y=False);

		self.voltPlot = self.win.addPlot(title="Voltage Reference", labels={'left':('Voltage', 'V'), 'bottom':('Time', 's')}, row=3, col=0);
		self.voltPlot.setMouseEnabled(x=False, y=False);
		self.voltPlot.enableAutoRange(x=True, y=True);

	def setupDataBuffers(self):
		self.refBuffer = np.zeros(self.numSamples);
		self.tempBuffer = np.zeros(self.numSamples);
		self.vapBuffer = np.zeros(self.numSamples);
		self.voltBuffer = np.zeros(self.numSamples);


	def setupCurves(self):
		self.refCurve = self.refPlot.plot(x=self.xData, y=self.refBuffer);
		self.tempCurve = self.tempPlot.plot(x=self.xData, y=self.tempBuffer);
		self.vapCurve = self.vapPlot.plot(x=self.xData, y=self.vapBuffer);
		self.voltCurve = self.voltPlot.plot(x=self.xData, y=self.voltBuffer);

	def updateDataBuffers(self, data):
		refData = data[:,0];
		tempData = data[:,1];
		vapData = data[:,2];
		voltData = data[:,3];
		numShift = len(refData);

		self.refBuffer = np.roll(self.refBuffer, -1*numShift, axis=0);
		self.tempBuffer = np.roll(self.tempBuffer, -1*numShift, axis=0);
		self.vapBuffer = np.roll(self.vapBuffer, -1*numShift, axis=0);
		self.voltBuffer = np.roll(self.voltBuffer, -1*numShift, axis=0);

		self.refBuffer[-numShift:] = refData;
		self.tempBuffer[-numShift:] = tempData;
		self.vapBuffer[-numShift:] = vapData;
		self.voltBuffer[-numShift:] = voltData;

	def updateCurves(self):
		self.refCurve.setData(x=self.xData, y=self.refBuffer);
		self.tempCurve.setData(x=self.xData, y=self.tempBuffer);
		self.vapCurve.setData(x=self.xData, y=self.vapBuffer);
		self.voltCurve.setData(x=self.xData, y=self.voltBuffer);

	def updateRoutine(self):
		data = self.dataBuffer.get(block=True, timeout=GraphWindow.QUEUE_TIMEOUT);
		self.updateDataBuffers(data);
		self.updateCurves();

	def run(self):
		if(self.isAlive):
			try:
				self.updateRoutine();
			except queue.Empty, OSError:
				self.isAlive = False;

			current = time.time();
			deltaTime = current - self._lastTime;
			self._lastTime = current;
			pg.QtCore.QTimer.singleShot(max((self._refreshPeriod-deltaTime)*1000, 1), self.run);
			# print(max((self._refreshPeriod-deltaTime)*1000, 1));
		else:
			return;

	def closeEvent(self, event):
		print("Closing");
		event.accept();
		self.stop();
		self.win.close();
		if(not self.stopFcn == None):
			self.stopFcn();

	def stop(self):
		self.isAlive = False;

	def closeWindow(self):
		self.win.close();


