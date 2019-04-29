import code
import TemperatureSystem

temperature = None;

def start(filename=None, device='/dev/ttyUSB0'):
	global temperature;
	temperature = TemperatureSystem.TemperatureSystem(device, filename);
	temperature.start();

def stop():
	global temperature;
	if(not temperature == None):
		temperature.stop();
	temperature = None;

def getFs():
	temperature.measureFs();

print("Starting Up...");
code.interact(local = locals());