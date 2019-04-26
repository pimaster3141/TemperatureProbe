import numpy as np

class QVConveter:
	def __init__(self, fullscale=3.3, span=65535):
		self.fullscale = fullscale;
		self.span = span;

	def convert(self, LSB):
		return LSB * self.fullscale / self.span;

class VRConverter:
	def __init__(self, vBias, rBias):
		self.vBias = vBias;
		self.rBias = rBias;

	def convert(self, vIn, vBias=None):
		if(vBias == None):
			vBias = self.vBias;
		return ((vIn - vBias) * self.rBias/vBias);


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



