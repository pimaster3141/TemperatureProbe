import setuptools
import pyximport; pyximport.install()
import threading
import numpy as np
import queue
import Converters

class DataProcessor(threading.Thread):
	QUEUE_TIMEOUT = 1;
	QUEUE_DEPTH = 100;

	FULLSCALE_VOLTAGE = 3.3;

	def __init__(self, MPI, inputBuffer, fs, bufferSize, rBias=[None, None] , STCoeff=[None, None]):
		threading.Thread.__init__(self);

		self.MPI = MPI;
		self.inputBuffer = inputBuffer;
		self.fs = fs;

		self.vBias = vBias;
		self.QVConverter = Converters.QVConverter();
		self.VRConverter = [None, None];
		self.RTConverter = [None, None];
		for i in range(2):
			if(not rBias[i] == None):
				self.VRConverter[i] = Converters.VRConverter(self.vBias, rBias[i]);
				self.RTConverter[i] = Converters.RTConverter3(STCoeff[i][1], STCoeff[i][2], STCoeff[i][3]);

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

				output[:,0] = np.mean(data[:, 0::4], 1);
				output[:,1] = np.mean(data[:, 1::4], 1);
				output[:,2] = np.mean(data[:, 2::4], 1);
				output[:,3] = np.mean(data[:, 3::4], 1);

				output = self.QVConverter.convert(output);

				if (not self.VRConverter[0] == None):
					output[:,0] = self.RTConverter[0].convert(self.VRConverter[0].convert(output[:,0], vBias=output[:,4]));
				if (not self.VRConverter[1] == None):
					output[:,1] = self.RTConverter[1].convert(self.VRConverter[1].convert(output[:,1], vBias=output[:,4]));

				try:
					self.dataBuffer.put_nowait(output);
				except queue.Full:
					pass;

		except Exception as e:
			# print("SHITBALLS IM MURDERED");
			# raise(e);
			try:
				self.MPI.put_nowait(e);
			except Exception as ei:
				pass
		finally:			
			self.shutdown();

	def shutdown(self):
		self.isDead.set();	
		
		time.sleep(0.5);
		while(True):
			try:
				(self.dataBuffer.get(False));
			except queue.Empty:
				time.sleep(0.5)    # Give tasks a chance to put more data in
				if not self.dataBuffer.empty():
					continue
				else:
					break;

		self.dataBuffer.close();
		self.dataBuffer.cancel_join_thread();
		try:
			self.MPI.put_nowait("Stopping Processor");
			time.sleep(0.5);
		except Exception as ei:
			pass
		finally:
			self.MPI.close();
			self.MPI.cancel_join_thread();

	def getBuffer(self):
		return self.dataBuffer;


