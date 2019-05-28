import numpy as np

class QVConverter:
	def __init__(self, fullscale=3.3, span=65535):
		self.fullscale = fullscale;
		self.span = span;

	def convert(self, LSB):
		return LSB * self.fullscale / self.span;

class VRConverterLive:
	def __init__(self, rBias, alpha=0.005):
		self.rBias = rBias;
		self.alpha = alpha;
		self.vBias = 0;

	def convert(self, vIn, vBias):
		# if(vBias == None):
		# 	vBias = self.vBias;
		vBias = np.mean(vBias);
		self.vBias = vBias*self.alpha + self.vBias*(1-self.alpha);
		return ((vIn - self.vBias) * self.rBias/self.vBias);

class VRConverter:
	def __init__(self, rBias):
		self.rBias = rBias;

	def convert(self, vIn, vBias):
		return ((vIn - vBias) * self.rBias/vBias);



# class RTConverter3:
# 	def __init__(self, A, B, C):
# 		self.A = A;
# 		self.B = B;
# 		self.C = C;

# 	def convert(self, rIn):
# 		rIn = np.maximum(rIn, 1E-10);

# 		output = self.A + self.B*np.log(rIn) + self.C*np.power(np.log(rIn), 3);
# 		return 1/output - 273.15;


# class RTConverter4:
# 	def __init__(self, A, B, C, D):
# 		self.A = A;
# 		self.B = B;
# 		self.C = C;
# 		self.D = D;

# 	def convert(self, rIn):
# 		rIn = np.maximum(rIn, 1E-10);

# 		output = self.A + self.B*np.log(rIn) + self.C*np.power(np.log(rIn), 3) + self.D*np.power(np.log(rIn), 5);
# 		return 1/output - 273.15;


class RTConverter:
	def __init__(self, coeff):
		self.A = coeff[0];
		self.B = coeff[1];
		self.C = coeff[2];
		if(len(coeff) == 3):
			self.D = 0;
		else:
			self.D = coeff[3];

	def convert(self, rIn):
		rIn = np.maximum(rIn, 1E-10);

		output = self.A + self.B*np.log(rIn) + self.C*np.power(np.log(rIn), 3) + self.D*np.power(np.log(rIn), 5);
		return 1/output - 273.15;



