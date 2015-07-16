#import os
#import glob
#import RPi.GPIO as io
import DS18B20

DS18B20.init()
thermometers = DS18B20.discover()
print thermometers

print DS18B20.read_temp_c(thermometers[0])
