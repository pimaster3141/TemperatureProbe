# Program to convert Voltage to Resistance from the TIA
# USAGE:
# 	Converter is instantiated as an object per Channel. 
#		Base Conversion Equation is:
#		R = (V - Vb) * Rb/Vb

import numpy as np
import math

class Converter: 
	
	#	Object Delcaration
	#		@Param:
	#			Vb - Optional Parameter to override default constant in Volts
	#			Rb - Optional Parameter to override default Resistance
	def __init__(self, Vb = 1, Rb = 1):
		self.Vb = Vb
		self.Rb = Rb
	

	#	Conversion Function
	#		@Param:
	#			voltage in Volts
	#		@Return:
	#			Resistance measurement in Ohms
	def getR(self, voltage):
		return ((voltage - self.Vb)*self.Rb/self.Vb)

	def getVb(self):
		return self.Vb

	#	Manual Coefficient setting
	#		@Param:
	#			Vb, Rb - Externally provided parameters to use as the coefficients
	#		@Return:
	#			None
	def setCoefficients(self, Vb, Rb):
		self.Vb = Vb
		self.Rb = Rb


