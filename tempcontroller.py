#!/usr/bin/python3

#This is a very simple temperature controller using a Raspberry Pi, DS18B20 thermometers, an Adafruit 4x8 Segment LED I2C backpack and a 5v controlled optocoupler 240v/120v relay
#Eventually this system will function as a web-enabled sous vide/slow cooker with a couple of extra components (Flame Detector, buzzer, maybe a smoke detector)

import os
import glob
try:
    import cPickle as pickle                  ## At some point I'm going to have the system remember preferences, such as thermometer designations
except:
    import pickle
import time
import datetime
from Adafruit_7Segment import SevenSegment     ## I will probably switch to an Adafruit 16x2 LCD Shield.  I've got the parts, I just need to get everything wired
import RPi.GPIO as io


log_dir = '/home/pi/SV/'                        ## Where we're going to keep log and configuration files
ConfigFile = "ConfigFile.PCK"                   ## The name of the configuration file, not used yet
log_path = (log_dir + ConfigFile)
Thermos ={}                                     ## We're going to put the thermometers in a dictionary.  This will let us easily designate thermometers
x= 0                                            ## that are used in the cooking process, external thermometers and "other"
designation = ""                                ## Right now the system is coded to look for "Cooking" thermometers, I plan to implement external thermometers as well
TargetTemp = 58.5                               ## Target temp in Centigrade.  Learn metric, people!
LoBuffer = 58.0                                 
HiBuffer = 58.6
CheckPeriod = 1                                 ## Currently I'm checking the temperature about every second
io.setmode(io.BCM)
power_pin = 18                                  ## The relay control pin for the rice cooker
z = 0
io.setup(power_pin, io.OUT)
io.output(power_pin, False)
pre_heat = 1
CookTime = 1
ErrorSum = 0
ErrorLast = 0


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'               ## Base directory for the DS18B20 thermometers.  This will let the Pi automatically check for connected DS18B20's
thermometers = (glob.glob(base_dir + '28*'))
print(thermometers)                             ## I'm leaving this "check" in for now.  This prints the listing of all of the thermometers.

for item in thermometers:                       ## Assigns a "null" value to the Key:Value pair for each thermometer.  I had a reason for doing this.  Can't remember
    thermometer = thermometers[x]
    Thermos[thermometer] = 'null'
    x=x+1
    
for key in Thermos:                             # This asks the user to designate a type to each thermometer.  Not validated for expansion
    print("Acceptable designations are: Cooking, External, Disregard")
    print(key, " Designation?",)
    designation = raw_input(">>> ")
    print (key, " is ", designation, ".  Got it!")
    Thermos[key] = designation

print(Thermos)

def read_temp_raw(thermometer):                 # This is almost line for line taken from Adafruit's tutorial on reading a DS18B20 from a Pi
    thermometer = thermometer + '/w1_slave'     # Two differences.  First, I read for the thermometer that is passed to the function
    f = open(thermometer, 'r')
    time.sleep(0.2)
    line1 = f.readline()
    line2 = f.readline()                        # Second, I break the lines into two separate lines, only passing the second line (where the temp is)
    f.close()
    return line2

def read_temp(thermometer):                     # Again, this is based off of the Adafruit tutorial.  I had some problems, I think because I pass  the
    lines = str(read_temp_raw(thermometer))     # thermometer to the function.
    temp_pos = lines.find('t=')
    temp_string = lines[temp_pos+2:]
    temp_float = (float(temp_string)) / 1000.0
    return temp_float


def CheckCookTemp():                            # This is designed to check multiple cooking thermometers and average them.  That hasn't been tested.
    x = 0.0                                     # So far this has only been tested with a single cooking thermometer
    TempTempC = 0.0
    TempTempF = 0.0
    CumTemp = 0.0
    AvgTemp = 0.0
    for key in Thermos:
        if Thermos[key] == 'Cooking':
            TempTempC = 0
            x = x + 1.0
            TempTempC = read_temp(key)
            CumTemp = CumTemp + TempTempC
    AvgTemp = CumTemp / x
    return AvgTemp

def ShowTemp(Temp):                             # This gave me fits.  The function is supposed to display the current temp on the 4x8 Segment LED Backpack
    segment = SevenSegment()                    # I had to play around with ranges and string slicing to make sure that I didn't get out of range errors
    StrTemp = str(Temp)                         # I thought about using some error catching here, but skull sweated it out.
    StrTemp = StrTemp[0:6]
    i = 0
    for i in range(5):
        if len(StrTemp) == 5:
            StrTemp = StrTemp + '0'
        if len(StrTemp) == 4:
            StrTemp = StrTemp + '00'
        if len(StrTemp) == 3:
            StrTemp = StrTemp + '000'
        if StrTemp[i] == '.':
            segment.writeDigit(i-1, int(StrTemp[i-1]), dot=True)
        elif StrTemp[i] != '.':
            segment.writeDigit(i, int(StrTemp[i]), dot=False)

                       

def PreHeat(pre_heat):                                  # Preheat cycle.  Once I start using PID controlling or some other scheme, this is probably going to change
    while pre_heat == 1:
        CurrentTemp = CheckCookTemp()
        z=0
        print (CurrentTemp)
        ShowTemp(CurrentTemp)
        io.output(power_pin, True)
        print 'Power On'
        if CurrentTemp > (TargetTemp - 10):
            LastTime = time.time()
            #PIDCook(TargetTemp, CurrentTemp, CurrentTime, Kp, Ki, Kd, ErrorSum, ErrorLast)  # This jumps us out of the PreHeat Function and into the cook function. 
            Cook()

        time.sleep(CheckPeriod)
        pre_heat = 1

#def PIDCook(TargetTemp, CurrentTemp, LastTime, Kp, Ki, Kd, ErrorSum, ErrorLast, CheckPeriod):
    #while CookTime == 1:
#        CurrentTime = time.time()
#        TimeDelta = CurrentTime - LastTime
#        CurrentTemp = CheckCookTemp()
#        Error =  TargetTemp - CurrentTemp
#        ErrorSum += (Error * TimeDelta)
#        dError = (Error - ErrorLast) / TimeDelta
#        Output = Kp * Error + Ki * ErrorSum + Kd * dError
#        ShowTemp(CurrentTemp)
#        print Output
#        #while TimeDelta < CheckPeriod:
        #    time.sleep(0.01)
        #    CurrentTime = time.time()
        #    TimeDelta = CurrentTime - LastTime
#        ErrorLast = Error
#        LastTime = CurrentTime
        #CookTime == 1


def Cook():
    while CookTime == 1:
        CurrentTemp = CheckCookTemp()
        CurrentTime = time.time()
        ShowTemp(CurrentTemp)
        #PIDCook(TargetTemp, CurrentTemp, CurrentTemp, Kp, Ki, Kd, ErrorSum, ErrorLast, CheckPeriod)
        print CurrentTemp,
        if CurrentTemp < (TargetTemp - 10):
            io.output(power_pin, True)
            time.sleep(20)
            if CurrentTemp < (TargetTemp - 5):
                io.output(power_pin, False)
            print "Heat Level 5"
        elif CurrentTemp < (TargetTemp - 5):
            io.output(power_pin, True)
            time.sleep(30)
            io.output(power_pin, False)
            time.sleep(1)
            print "Heat Level 4"
        elif CurrentTemp < (TargetTemp - 1):
            io.output(power_pin, True)
            time.sleep(20)
            io.output(power_pin, False)
            time.sleep(1)
            print "Heat Level 3"
        elif CurrentTemp < (TargetTemp - .5):
            io.output(power_pin, True)
            time.sleep(10)
            io.output(power_pin, False)
            time.sleep(1)
            print "Heat Level 2"
        elif CurrentTemp < (TargetTemp - .2):
            io.output(power_pin, True)
            time.sleep(5)
            io.output(power_pin, False)
            time.sleep(1)
            print "Heat Level 1"
        elif CurrentTemp < (TargetTemp):
            io.output(power_pin, False)
            print "Not Heating, low"
            time.sleep(1)
        elif CurrentTemp == (TargetTemp):
            io.output(power_pin, False)
            print "Not Heating, Right on"
        elif CurrentTemp > (TargetTemp):
            io.output(power_pin, False)
            time.sleep(1)
            print "Not Heating, high"
    CookTime == 1
    


PreHeat(1)

