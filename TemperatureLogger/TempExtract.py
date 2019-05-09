import numpy as np

PROBE_CALIBRATION = [  1.70870768e-04,   2.77265018e-04,  -3.08921532e-07,  6.58941403e-10]

def fullExtractMatlab(filename, probeConstants=PROBE_CALIBRATION, fs=None):
	if(fs == None):
		with open(filename+'.params') as temp:
			value = temp.readline();
			fs = int(''.join(list(filter(str.isdigit, value))));
		print("Autoelecting fs: "+str(fs));

	print("Extracting: " + filename);
	