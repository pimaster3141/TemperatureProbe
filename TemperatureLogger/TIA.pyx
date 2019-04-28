import multiprocessing as mp
import serial
import queue
import psutil
import array
import os
import time

class TIADriver(mp.Process):
	_HEADER = 0XAA;
	_START_BYTE = 0X61;
	_STOP_BYTE = 0X62;
	_PAYLOAD_SIZE = 8*100;

	_BAUD = 2000000;
	_TIMEOUT = 1;


	def __init__(self, MPI, port):
		mp.Process.__init__(self):

		self.MPI = MPI;

		self.serial = serial.Serial(port=None, baudrate=_BAUD, timeout=_TIMEOUT);
		self.serial.port = port;
		self.serial.open();

		(self.pipeOut, self.pipeIn) = mp.Pipe(duplex=False);

		self._packet = array.array('b', [0]*_PAYLOAD_SIZE);

		self.sampleCounter = mp.Value('L', 0);
		self.startTime = mp.Value('f', 0.0);

		self.isDead = mp.Event();


	def run(self):
		p = psutil.Process(os.getpid());
		p.nice(-15);

		self.resetBuffer();
		self.startTrans();
		self.startTime.value = time.time();

		try:
			while(not self.isDead.is_set()):
				d = self.serial.read_until(bytes([_HEADER]));
				numRead = self.serial.readinto(self._packet);

				if((numRead) != _PAYLOAD_SIZE):
					raise Exception("Device not ready");

				self.pipeIn.send_bytes(self._packet);

				c = self.sampleCounter.value;
				self.sampleCounter.value = c + 1;

		except Exception as e:
			try:
				self.MPI.put_nowait(e);
			except Exception as ei:
				pass
		finally:
			self.shutdown();

	def shutdown(self):
		self.isDead.set();
		try:
			self.MPI.put_nowait("Stopping Driver");
			self.serial.close();
		except Exception as ei:
			pass
		finally:
			self.MPI.close();
			self.MPI.cancel_join_thread();

	def stop(self):
		if(not self.isDead.is_set()):
			self.isDead.set();
			self.join();
		
	def getPipe(self):
		return self.pipeOut;


	def startTrans(self):
		self.serial.write([_START_BYTE]);
		self.serial.flush();

	def stopTrans(self):
		self.serial.write([_STOP_BYTE]);
		self.serial.flush();
		time.sleep(2);

	def resetBuffer(self):
		self.serial.reset_input_buffer();

	def getSampleRate(self):
		currentTime = time.time();
		samples = self.sampleCounter.value;
		startTime = self.startTime.value;

		return int(samples/(currentTime-startTime));

	def resetSampleRate(self):
		self.sampleCounter.value = 0;
		self.startTime.value = time.time();