import numpy as np

class VRConverter:
	def __init__(self, vBias, rBias):
		self.vBias = vBias;
		self.rBias = rBias;

	def convert(self, vIn):
		return ((vIn - self..vBias) * self.rBias/self.vBias);


class RTConverter3:
	def __init__(self, A, B, C):
		self.A = A;
		self.B = B;
		self.C = C;

	def convert(self, rIn):
		rIn = np.maximum(rIn, 1E-10);

		output = self.A + self.B*np.log(rIn) + self.C*np.power(np.log(rIn), 3);
		return 1/output - 273.15;


class RTConverter4:
	def __init__(self, A, B, C, D):
		self.A = A;
		self.B = B;
		self.C = C;
		self.D = D;

	def convert(self, rIn):
		rIn = np.maximum(rIn, 1E-10);

		output = self.A + self.B*np.log(rIn) + self.C*np.power(np.log(rIn), 3) + self.D*np.power(np.log(rIn), 5);
		return 1/output - 273.15;



