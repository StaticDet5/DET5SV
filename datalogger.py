#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from numpy import *
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import cPickle as pickle


def log_line(level,loginfo, logfile = 'SensorLog2.log'):
    protocol = pickle.HIGHEST_PROTOCOL
    log = open(logfile, 'ab+')
    epochtime = time.time()
    realtime = time.asctime()
    logtime = {'Date':realtime}
    loginfo.update(logtime)
    timemark = {'Time': epochtime}
    loginfo.update(timemark)
    loglevel = {'Level': level}
    loginfo.update(loglevel)
    pickle.dump(loginfo, log, protocol)
    log.close()


def log_read(logfile = 'SensorLog2.log'):
    log = open(logfile, 'rb')
    testval = True
    loglist = []
    x = 0
    while testval == True:
        try:
            x = x + 1
            b = pickle.load(log)
            loglist.append(b)
            b = {}
        except:
            testval == False
            break
    log.close()
    return loglist, x-1

#def log_length(logfile = 'SensorLog.log'):
#    log = open(logfile, 'r')
#    testval = True
#    loglist = []
#    x = 0
#    while testval == True:
#        try:
#            x = x + 1
#            b = pickle.load(log)
#            loglist.append(b)
#            b = {}
#        except:
#            testval == False
#            break
#    return x-1              #it appears that the first record in the pickle isn't log data

def log_param_list(parameter, filler = 'NULL', logfile = 'SensorLog2.log'):
    loglist, length = log_read(logfile) 
#    length = log_length(logfile)
    parameterlist=[]
    x=0
    for i in range(length):
        #print(i)
        c = loglist[i]
        if parameter in c:
            pulledvalue = c[parameter]
            parameterlist.append(pulledvalue)
            #print('Found', parameter, ' at ', i)
        else:
            #print('Not found')
            if filler != 'NULL':
                parameterlist.append(filler)
            #print('Filler ', filler, ' appended')
            #else:
                #print('Nothing appended')
    return parameterlist

def entry_level(logentry):
    temp1limits = {'critlow' : 0, 'warnlow' : 12, 'warnhigh' : 25, 'crithigh' : 30}
    temp2limits = {'critlow' : 0, 'warnlow' : 12, 'warnhigh' : 25, 'crithigh' : 30}
    info = 'Info'
    if 'temp1' in logentry:
        temp1 = logentry['temp1']
        if temp1 < temp1limits['critlow'] or temp1 > temp1limits['crithigh']:
            info = 'Critical'
        elif temp1 < temp1limits['warnlow'] or temp1 > temp1limits['warnhigh']:
            info = 'Warning'
    if 'temp2' in logentry and info != 'Critical':
        temp2 = logentry['temp2']
        if temp2 < temp2limits['critlow'] or temp2 > temp2limits['crithigh']:
            info = 'Critical'
        elif temp2 < temp2limits['warnlow'] or temp2 > temp2limits['warnhigh']:
            info = 'Warning'
    if info == 'Critical':
        info = 'Critical'
    elif info == 'Warning':
        info = 'Warning'
    else:
        info = 'Info'
    return info

def genchart(parameter, length = 1440, filler = 'NULL', logfile = 'SensorLog2.log', chartfile = 'Chart.png'):
    #parameterlength = log_length(logfile)
    parameterlist = log_param_list(parameter, filler, logfile)
    parameterlength = len(parameterlist)
    if length > parameterlength:
        length = parameterlength
    start = parameterlength - length
    end = parameterlength
    chartlist = parameterlist[start:end]
    plt.plot(chartlist, label=parameter)
    plt.legend()
    plt.savefig(chartfile)
    plt.close()
