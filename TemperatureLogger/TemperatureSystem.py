from sys import platform
if platform == "linux" or platform == "linux2":
    pass
elif platform == "darwin":
    raise Exception("Unsupported OS: " + str(platform));
elif platform == "win32":
    raise Exception("Unsupported OS: " + str(platform));

print("Compiling and Loading Libraries...")

import setuptools
import pyximport; pyximport.install()

import TIA
import TempHandler
import TempProcessor
import TempDisplay
import multiprocessing as mp
import time

print("Done");

class TemperatureSystem():
	BIAS_RESISTORS = [10E3, 24E3];
	ST_COEFF=[[6.71742703E-04, 2.20416992E-04, 9.98713347E-08, -4.61649439E-11],
		[  1.70870768e-04,   2.77265018e-04,  -3.08921532e-07,  6.58941403e-10]]

	def __init__(self, device, outFile=None, directory='./output/'):
		self.outFile = outFile;
		self.directory = directory;
		if (directory == None):
			directory = './output/';
		if(not(directory[-1] == '/')):
			self.directory = directory + '/'

		self.MPITIA = mp.Queue();
		self.MPIHandler = mp.Queue();
		self.MPIProcessor = mp.Queue();

		self.TIA = TIA.TIADriver(self.MPITIA, device);
		tiaPipe = self.TIA.getPipe();
		self.handler = TempHandler.DataHandler(self.MPIHandler, tiaPipe, TIA.TIADriver._PAYLOAD_SIZE, filename=outFile, directory=directory);
		self.handler.pause();
		self.handler.start();
		self.TIA.start();

		print("Benchmarking ~10s");
		time.sleep(10);
		self.fs = self.TIA.getSampleRate();

		handlerBuffer = self.handler.getRealtimeQueue();
		self.handler.enableRealtime();
		self.processor = TempProcessor.DataProcessor(self.MPIProcessor, handlerBuffer, TIA.TIADriver._PAYLOAD_SIZE, rBias=TemperatureSystem.BIAS_RESISTORS, STCoeff=TemperatureSystem.ST_COEFF);

	def stop(self):
		print("Halting Device");

		self.readAllMPI();
		self.TIA.stop();
		self.handler.stop();
		self.processor.stop();
		self.display.stop();

		self.TIA.join();
		self.handler.join();
		self.processor.join();

		self.readAllMPI();

		print("Device Halted");

	def start(self):
		print("Starting Collection");
		print("Device is " + str(self.fs/1E3) + "Ksps");
		if(not self.outFile == None):
			# with open(str(self.directory + self.outFile)+".params", "w") as f:
			# 	f.write("fs="+str(self.fs)+"\n");
			np.savez(str(self.directory + self.outFile), BIAS_RESISTORS=TemperatureSystem.BIAS_RESISTORS, ST_COEFF=TemperatureSystem.ST_COEFF, fs=self.fs);
		self.processor.start();
		self.handler.resume();
		processorBuffer = self.processor.getBuffer();
		self.display = TempDisplay.GraphWindow(processorBuffer, self.fs*8.0/TIA.TIADriver._PAYLOAD_SIZE, stopFcn=self.stop);
		self.display.run();
		print("Device running");

	def measureFs(self):
		fs = self.TIA.getSampleRate();
		print("Device is " + str(fs/1E3) + "Ksps");



	def readAllMPI(self):
		s = self.MPITIA.qsize();
		for i in range(s):
			try:
				print(self.MPITIA.get(False));
			except Exception as e:
				print("WARNING: ")
				print(e);
				continue;

		# print("");
		s = self.MPIHandler.qsize();
		for i in range(s):
			try:
				print(self.MPIHandler.get(False));
			except Exception as e:
				print("WARNING: ")
				print(e);
				continue;

		# print("");
		s = self.MPIProcessor.qsize();
		for i in range(s):
			try:
				print(self.MPIProcessor.get(False));
			except Exception as e:
				print("WARNING: ")
				print(e);
				continue;
		
