import serial
import threading
import queue
import time
import VR
import multiprocessing as mp

HEADER = 170
FULLSCALE = 3.307
R_BIAS = [73200, 73200, 73200, 73200]


class TIABuffer(threading.Thread):
# class TIABuffer(mp.Process):
	def __init__(self, port, decimationFactor):
		threading.Thread.__init__(self)
		# mp.Process.__init__(self)
		self.COM = serial.Serial(port=port, baudrate=2000000)
		self.COM.timeout = 1
		# self.COM.open()
		self.downsample = decimationFactor
		self.outputBuffer = queue.Queue()
		self.isAlive = True
		self.sampleRate = 5000
		self.VRConverter = []
		for i in range(4):
			self.VRConverter.append(VR.Converter())

		self.calibrate()
		print("SampleRate = " + str(self.sampleRate) + "sa/sec")
		print("Calibration Data: ")
		for i in range(len(self.VRConverter)):
			print("\tChannel", i,": ", self.VRConverter[i].getVb())

	def getSampleRate(self):
		return self.sampleRate

	def setDecimation(self, value):
		self.downsample = int(value)


	def startTrans(self):
		self.COM.write(chr(97).encode())
		self.COM.flush()

	def stopTrans(self):
		self.COM.write(chr(98).encode())
		self.COM.flush()
		time.sleep(2)

	def resetBuffer(self):
		self.COM.reset_input_buffer()

	def run(self):
		payload = bytes()
		packets = []
		while(self.isAlive):
			inBuffer = int(self.COM.inWaiting() / 9)

			if(inBuffer < 9):
				inBuffer = 9

			payload = payload + self.COM.read(inBuffer)

			if(len(payload) == 0):
				continue

			if(len(payload) < 9):
				print("Incomplete Packet")
				self.findStart()
				payload = bytes()
				packets = []
				continue

			if(payload[0] != HEADER):
				print("Framing Error, flushing")
				print(list(payload)[0:10])
				self.findStart()
				payload = bytes()
				packets = []
				continue

			for count in range(int(len(payload) / 9)):
				packets.append(self.parsePacket(payload[:9]))
				payload = payload[9:]

			for count in range(int(len(packets) / self.downsample)):
				values = (self.decimate(packets[:self.downsample]))
				values = self.VRConvert(values)
				self.updateBuffer(values)
				packets = packets[self.downsample:]


			# for count in range(int(len(payload) / (self.downsample*9))):
			# 	self.updateBuffer(self.decimate(payload[:self.downsample*9]))
			# 	payload = payload[self.downsample*9:]




	def findStart(self):
		# time.sleep(.2)
		print("finding Start")
		current = self.COM.read(1)[0]
		while(current != HEADER and self.isAlive):
			current = self.COM.read(1)[0]
		self.COM.read(8)

	def parsePacket(self, payload):
		payload = list(payload)
		payload.pop(0)
		packet = []
		for i in range(4):
			MSB = (payload.pop(0))
			LSB = (payload.pop(0))
			packet.append(((MSB << 8) + LSB) * FULLSCALE / 65535)

		return packet 

	def decimate(self, data):
		output = [0,0,0,0]
		counter = 0;

		for packet in data:
			for i in range(len(packet)):
				output[i] = output[i] + packet[i]
			counter = counter + 1




		# for i in range(int(len(data)/9)):
		# 	packet = self.parsePacket(data[:9])
		# 	for p in range(len(packet)):
		# 		output[p] = output[p] + packet[p]
		# 	data = data[9:]
		# 	counter = counter + 1

		for i in range(len(output)):
			output[i] = output[i]/float(counter)

		if (counter != self.downsample):
			raise Exception
		# print(output)
		return output

	def VRConvert(self, data):
		output = [0,0,0,0]
		for i in range(len(data)):
			output[i] = self.VRConverter[i].getR(data[i])
		return output

	def updateBuffer(self, data):
		# print(data)
		self.outputBuffer.put(data)

	def readBuffer(self):
		output = self.outputBuffer.get()
		# print(output)
		return output


	def stop(self):
		self.isAlive = False
		try:
			self.join()
		except:
			pass
		self.COM.close()

	def inBuffer(self):
                return self.outputBuffer.qsize()

	def calibrate(self):
		print("collecting data for 10s")
		self.stopTrans()
		self.resetBuffer()

		byteCount = 0
		self.startTrans()
		startTime = time.clock()
		payload = []
		data = [[],[],[],[]]

		while(time.clock() - startTime < 10):
			waiting = self.COM.inWaiting()
			byteCount = byteCount + waiting
			# byteCount = byteCount + 10000
			payload = payload + list(self.COM.read(waiting))
			while(len(payload) > 9):
				if(payload[0] == HEADER):
					processed = self.parsePacket(payload[:9])
					for i in range(len(processed)):
						data[i].append(processed[i])
					payload = payload[9:]
				else:
					payload.pop(0)

		self.stopTrans()
		stopTime = time.clock()
		byteCount = byteCount + self.COM.inWaiting()
		self.COM.reset_input_buffer()
		# byteCount = byteCount + 10000
		# print(byteCount)

		accumulator = [0,0,0,0]
		for i in range(len(accumulator)):
			for j in range(len(data[i])):
				accumulator[i] = accumulator[i] + data[i][j]

		for i in range(len(accumulator)):
			self.VRConverter[i].setCoefficients(accumulator[i]/float(len(data[i])), R_BIAS[i])

		self.sampleRate = (byteCount / 9.0) / (stopTime - startTime)



