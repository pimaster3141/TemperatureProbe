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
import DataHandler
import DataProcessor
import Display
import multiprocessing as mp

print("Done");

class TemperatureSystem():

	def __init__(self, device, outFile=None):
		self.outFile = outFile;

		self.MPITIA = mp.Queue();
		self.MPIHandler = mp.Queue();
		self.MPIProcessor = mp.Queue();

		
