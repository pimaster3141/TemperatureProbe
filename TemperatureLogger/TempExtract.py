import setuptools
import pyximport; pyximport.install()
import numpy as np
import Converters
import os
import hdf5storage as matWriter

BIAS_RESISTORS = [10E3, 24E3];
ST_COEFF=[[6.71742703E-04, 2.20416992E-04, 9.98713347E-08, -4.61649439E-11],
		[  1.70870768e-04,   2.77265018e-04,  -3.08921532e-07,  6.58941403e-10]]

def fullExtractMatlab(filename):
	global BIAS_RESISTORS
	global ST_COEFF

	fs = None;
	if(os.path.isfile(filename+'.params')):
		with open(filename+'.params') as temp:
			value = temp.readline();
			fs = int(''.join(list(filter(str.isdigit, value))));
		print("Autoelecting fs: "+str(fs));

	elif(os.path.isfile(filename+'.npz')):
		npzfile = np.load(filename+'npz');
		BIAS_RESISTORS = npzfile['BIAS_RESISTORS'];
		ST_COEFF = npzfile['ST_COEFF'];
		fs = npzfile['fs'];
		print("Autoelecting fs: "+str(fs));
		print("Loaded Calibration Data");

	else:
		raise Exception("Missing Calibration Data (.params or .npz file)");


	print("Extracting: " + filename);

	data = None;
	with open(filename, 'rb') as f:
		data = np.fromfile(f, dtype=np.uint16);

	ref = data[0::4];
	probe = data[1::4];
	vap = data[2::4];
	voltage = data[3::4];

	QVC = Converters.QVConverter();
	ref = QVC.convert(ref);
	probe = QVC.convert(probe);
	vap = QVC.convert(vap);
	voltage = QVC.convert(voltage);

	limit = np.std(voltage);
	badpts1 = np.where(voltage>np.mean(voltage)+limit)[0];
	badpts2 = np.where(voltage<np.mean(voltage)-limit)[0];
	badpts = np.concatenate((badpts1,badpts2));
	meanRef = np.mean(ref);
	meanProbe = np.mean(probe);
	meanVap = np.mean(vap);
	meanVoltage = np.mean(voltage);
	ref[badpts] = meanRef;
	probe[badpts] = meanProbe;
	vap[badpts] = meanVap;
	voltage[badpts] = meanVoltage;

	VRref = Converters.VRConverter(BIAS_RESISTORS[0]);
	VRprobe = Converters.VRConverter(BIAS_RESISTORS[1]);
	RTref = Converters.RTConverter(ST_COEFF[0]);
	RTprobe = Converters.RTConverter(ST_COEFF[1]);

	ref = RTref.convert(VRref.convert(ref, voltage));
	probe = RTprobe.convert(VRprobe.convert(probe, voltage));


	print("Creating Matlab File: " + filename+'.mat');
	outData = {};

	outData['BIAS_RESISTORS'] = BIAS_RESISTORS;
	outData['ST_COEFF'] = ST_COEFF;
	outData['fs'] = fs;
	outData['reference'] = ref;
	outData['probe'] = probe;
	outData['vap'] = vap;
	outData['voltage'] = voltage;

	matWriter.savemat(filename, outData);

	print("Done");

def batchFullExtract(filenames):
	for f in filenames:
		fullExtractMatlab(f);

