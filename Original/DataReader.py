import queue

class Reader():

	def __init__(spoof=False, inFile='data'):
		self.spoof = spoof
		self.dataFile = inFile
		self.dataQueue = queue.Queue()

	def read(size=1, blocking=True):
		if (size < 1):
			raise Exception("Invalid arguments")

