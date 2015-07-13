#!/usr/bin/python

from Logger import *
from Adafruit_BMP085 import BMP085
from Ty_TMP102 import TMP102
from Ty_TSL2561 import TSL2561
import time


def poll():
    bmp = BMP085(0x77)
    tmp = TMP102(0x48)
    tsl = TSL2561(0x39)
    logentry = {}
    temp1 = {'temp1' :bmp.readTemperature()}
    logentry.update(temp1)
    temp2 = {'temp2' :tmp.readTemperature()}
    logentry.update(temp2)
    pressure1 = {'pressure1' :bmp.readPressure()}
    logentry.update(pressure1)
    light1 = {'light1' :tsl.readLux()}
    logentry.update(light1)


    info = entry_level(logentry)
    
    log_line(info, logentry)
    print(logentry['Date'],logentry['temp1'],logentry['temp2'])

x = 1
y=0
while x == 1:
    y=y+1
    poll()
    print(y)
    time.sleep(1)
