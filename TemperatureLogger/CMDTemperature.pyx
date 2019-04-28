import code
import TemperatureSystem

temperature = None;

def start(device, filename=None):
	global temperature;
	temperature = TemperatureSystem.TemperatureSystem(device, filename);
	temperature.start();

def stop():
	global temperature;
	if(not temperature == None):
		temperature.stop();
	temperature = None;

print("Starting Up...");
code.interact(local = locals());