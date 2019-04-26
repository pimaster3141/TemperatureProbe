# Program to convert resistance measurements to temperature using 3 point stein-steinhart.

# USAGE:
# 	Converter is instantiated as an object per thermistor. All temperatures are inputted/outputted as CELSIUS (Kelvin conversons handled internally)
#	Hart-Steinhart equation is:
#		T = 1/(A + B*ln(R) + C*ln(R)^3)

import numpy as np
import math

class RTThermistor: 
	
	#	Object Delcaration
	#		@Param:
	#			A, B, C - Optional Parameters to override default constants
	#			Name - Currently unused  
	def __init__(self, A = 1, B = 1, C = 0, Name=""):
		self.A = A
		self.B = B
		self.C = C
		self.name = Name
	

	#	Conversion Function
	#		@Param:
	#			res - Resistance measurement
	#		@Return:
	#			Temperature measurement in C
	def getTempC(self, res):
		if(res < 0):
			res = 1E-10
		output = self.A + self.B*math.log(res) + self.C*(math.log(res))**3
		return 1/output - 273.15

	#	Manual Coefficient setting
	#		@Param:
	#			A, B, C - Externally provided parameters to use as the coefficients for Hart-Steinhart
	#		@Return:
	#			None
	def setCoefficients(self, A, B, C):
		self.A = A
		self.B = B
		self.C = C

	#	Name Setting (not used)
	def setName(self, Name):
		self.name = Name

	#	Calibration Function
	#		Function takes a 3 point calibration measurement and updates internal coefficients
	#		@Param:
	#			res - a vector list of resistances of length 3 for specified temperatures
	#			temp - a vector list of temperatures of length 3 for specified resistances
	#		@return:
	#			Updates internal states for A,B,C
	#			Returns list of [A, B, C]
	def calibrate(self, res, temp):
		#data sanitation
		if (type(res) != list or type(temp) != list):
			raise TypeError
		if (len(res) != 3 and len(temp) != 3):
			raise ValueError

		# form a 3x3 coefficient matrix and a 1x3 solution matrix of form:
		#	[	1,	ln(r1),	ln(r1)^3			[	A 			
		#		1,	ln(r2),	ln(r2)^3		*		B 		=	[	1/t1,	1/t2,	1/t3	]
		#		1,	ln(r3),	ln(r3)^3	]			C 	]
		a = [[1],[1],[1]]
		b = []
		for i in range(3):
			a[i].append(math.log(res[i]))
			a[i].append(math.log(res[i])**3)
			b.append(1.0/float(temp[i]+273.15))

		# Solve for variable vector
		coeff = np.linalg.solve(a,b)

		# Update internal state
		self.A = coeff[0]
		self.B = coeff[1]
		self.C = coeff[2]

		return coeff




class RTThermistor4: 
	
	#	Object Delcaration
	#		@Param:
	#			A, B, C - Optional Parameters to override default constants
	#			Name - Currently unused  
	def __init__(self, A = 1, B = 1, C = 0, D = 0, Name=""):
		self.A = A
		self.B = B
		self.C = C
		self.D = D
		self.name = Name
	

	#	Conversion Function
	#		@Param:
	#			res - Resistance measurement
	#		@Return:
	#			Temperature measurement in C
	def getTempC(self, res):
		if(res < 0):
			res = 1E-10
		output = self.A + self.B*math.log(res) + self.C*(math.log(res))**3 + self.D*(math.log(res))**5
		return 1/output - 273.15

	#	Manual Coefficient setting
	#		@Param:
	#			A, B, C - Externally provided parameters to use as the coefficients for Hart-Steinhart
	#		@Return:
	#			None
	def setCoefficients(self, A, B, C, D):
		self.A = A
		self.B = B
		self.C = C
		self.D = D

	#	Name Setting (not used)
	def setName(self, Name):
		self.name = Name

	#	Calibration Function
	#		Function takes a 3 point calibration measurement and updates internal coefficients
	#		@Param:
	#			res - a vector list of resistances of length 3 for specified temperatures
	#			temp - a vector list of temperatures of length 3 for specified resistances
	#		@return:
	#			Updates internal states for A,B,C
	#			Returns list of [A, B, C]
	def calibrate(self, res, temp):
		#data sanitation
		if (type(res) != list or type(temp) != list):
			raise TypeError
		if (len(res) != 4 and len(temp) != 4):
			raise ValueError

		# form a 3x3 coefficient matrix and a 1x3 solution matrix of form:
		#	[	1,	ln(r1),	ln(r1)^3			[	A 			
		#		1,	ln(r2),	ln(r2)^3		*		B 		=	[	1/t1,	1/t2,	1/t3	]
		#		1,	ln(r3),	ln(r3)^3	]			C 	]
		a = [[1],[1],[1],[1]]
		b = []
		for i in range(4):
			a[i].append(math.log(res[i]))
			a[i].append(math.log(res[i])**3)
			a[i].append(math.log(res[i])**5)
			b.append(1.0/float(temp[i]+273.15))

		# Solve for variable vector
		coeff = np.linalg.solve(a,b)

		# Update internal state
		self.A = coeff[0]
		self.B = coeff[1]
		self.C = coeff[2]
		self.D = coeff[3]

		return coeff


