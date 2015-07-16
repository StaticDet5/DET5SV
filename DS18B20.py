
import os
import glob
import time
import RPi.GPIO as io

def init():
	os.system('modprobe w1-gpio')
	os.system('modprobe w1-therm')

def discover():
	base_dir = '/sys/bus/w1/devices/' 
	thermometers = (glob.glob(base_dir + '28*'))
	return thermometers

def read_temp_raw(thermometer):                 # This is almost line for line taken from Adafruit's tutorial on reading a DS18B20 from a Pi
    thermometer = thermometer + '/w1_slave'     # Two differences.  First, I read for the thermometer that is passed to the function
    f = open(thermometer, 'r')
    time.sleep(0.2)
    line1 = f.readline()
    line2 = f.readline()                        # Second, I break the lines into two separate lines, only passing the second line (where the temp is)
    f.close()
    return line2

def read_temp_c(thermometer):                     # Again, this is based off of the Adafruit tutorial.  I had some problems, I think because I pass  the
    lines = str(read_temp_raw(thermometer))     # thermometer to the function.
    temp_pos = lines.find('t=')
    temp_string = lines[temp_pos+2:]
    temp_float = (float(temp_string)) / 1000.0
    return temp_float