# hardwareInterfacer.py
# CRT
# created 5/14/2018
# last updated 5/14/2018
# provides miscellaneous utility functions

import time

def makeFileName(sensor):
    t = time.localtime()
    return 'RideLog_%s_%s.txt' % (time.strftime("%Y:%m:%d:%H:%M:%S", t), sensor)

def makeTimeStamp():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)

def writeToFile(fileName, data):
    with open(fileName, 'a') as f:
        f.write(data)

def checkWiFi():
    return True
