import PyQt5
import pyqtgraph as pg
import numpy as np

class GraphWindow():
	QUEUE_TIMEOUT = 5;

	def __init__(self, dataBuffer, sampleRate, depth=10, refreshRate=30):
		self.dataBuffer = dataBuffer;
		self.depth = depth;
		self.sampleRate = sampleRate;
		self.refreshRate = refreshRate;

		self.numSamples = self.depth * self.sampleRate;
		self.xData = np.arange(-self.numSamples, 0)/self.sampleRate;

	def setupPlots(self):
		self.win = pg.GraphicsWindow("Temperature");
		self.win.closeEvent = self.closeEvent;

		self.refPlot = self.win.addPlot(title="Reference Probe", labels={'left':('Temp', 'C'), 'bottom':('Time', 's')}, row=0, col=0);
		self.refPlot.setMouseEnabled(x=False, y=False);
		self.refPlot.enableAutoRange(x=True, y=True);
		self.refPlot.showGrid(x=True, y=True);

		self.tempPlot = self.win.addPlot(title="Temperature Probe", labels={'left':('Temp', 'C'), 'bottom':('Time', 's')}, row=0, col=0);
		self.tempPlot.setMouseEnabled(x=False, y=False);
		self.tempPlot.enableAutoRange(x=True, y=True);
		self.tempPlot.showGrid(x=True, y=True);

		self.vapPlot = self.win.addPlot(title="Vaporizer", labels={'bottom':('Time', 's')}, row=1, col=1);
		self.vapPlot.setMouseEnabled(x=False, y=False);

		self.voltPlot = self.win.addPlot(title="Voltage Reference", labels={'left':('Voltage', 'V'), 'bottom':('Time', 's')}, row=0, col=0);
		self.voltPlot.setMouseEnabled(x=False, y=False);
		self.voltPlot.enableAutoRange(x=True, y=True);

	def setupDataBuffers(self):
		self.refBuffer = np.zeros(self.numSamples)

	def setupCurves(self):

		self.refCurve = self.refPlot.plot(x=self.xData, y)
