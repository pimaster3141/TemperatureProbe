import threading
import numpy as np
import queue

class DataProcessor(threading.Thread):
	QUEUE_TIMEOUT = 1;
	QUEUE_DEPTH = 100;

	def __init__(self, MPI, inputBuffer, fs, bufferSize, vRef, rBias=[None, None, None, None], STCoeff=[None, None, None, None]):
		threading.Thread.__init__(self);

		self.MPI = MPI;
		self.inputBuffer = inputBuffer;
		self.fs = fs;

		self.vref = vref;
		


		self.npDtype = np.uint16;
		self.packetSize = int(bufferSize/2);

		self.dataBuffer = threading.Queue(DataProcessor.QUEUE_DEPTH);

		self.isDead = threading.Event();

	def run(self):
		try:
			initialData = np.zeros(self.packetSize, dtype=self.npDtype);
			while(not self.isDead.is_set()):
				try:
					initialData[0:] = self.inputBuffer.get(block=True, timeout=DataProcessor.QUEUE_TIMEOUT);
				except queue.Empty:
					continue

				inWaiting = self.inputBuffer.qsize();
				data = np.zeros((inWaiting+1, self.packetSize), dtype=self.npDtype);
				data[0] = initialData;

				output = np.zeros((inWaiting+1), 4);

				try:
					for i in range(inWaiting):
						data[i+1][0:] = self.inputBuffer.get(block=True, timeout=DataProcessor.QUEUE_TIMEOUT);
				except queue.Empty:
					pass

				for i in range(4):
					output[:,i] = np.mean(data[:, i::4], 1);


