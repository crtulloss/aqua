# hardwareInterfacer.py
# CRT
# created 5/14/2018
# last updated 5/16/2018
# provides miscellaneous utility functions

import time
import requests

# data logging spreadsheet settings
publicURL = 'https://script.google.com/macros/s/AKfycbxKm2AWyX6unin8LXDkbL7l1SUre2bDJNTTGUyMk9VhXmJRgMs/exec'
sheetName = 'aqua state machine tests'

# wifi check settings
wifiCheckTime = 30

def makeFileName(sensor):
    t = time.localtime()
    return 'RideLog_%s_%s.txt' % (time.strftime("%Y:%m:%d:%H:%M:%S", t), sensor)

def makeTimeStamp():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)

def writeToFile(fileName, data):
    with open(fileName, 'a') as f:
        f.write(data)

def uploadData(controllerInstance):
    gpsFileName = controllerInstance.gpsFileName
    accelFileName = controllerInstance.accelFileName
    fd = controllerInstance.freshData
    # if there is new data to log (i.e. we came back from a ride)
    if fd:
        # get the file contents and split into rows
        gpsFile = open(gpsFileName, 'r')
        gpsContents = gpsFile.read()
        gpsRows = gpsContents.split('\n')

        accelFile = open(accelFileName, 'r')
        accelContents = accelFile.read()
        accelRows = accelContents.split('\n')
        while fd:
            try:
                for row in gpsRows:
                    # split each row by data point
                    rowEntries = row.split('\t')
                    # make sure there are the correct number of entries
                    if (len(rowEntries) == 3):
                        # log the data
                        gpsData = {'sheet':sheetName+':GPS', 'Data Time':rowEntries[0], 'Latitude':rowEntries[1], 'Longitude':rowEntries[2]}
                        requests.get(publicURL, params=gpsData)
                for row in accelRows:
                    rowEntries = row.split('\t')
                    if (len(rowEntries) == 4):
                        accelData = {'sheet':sheetName+':Accel', 'Data Time':rowEntries[0], 'X':rowEntries[1], 'Y':rowEntries[2], 'Z':rowEntries[3]}
                        requests.get(publicURL, params=accelData)
                # no more fresh data
                fd = False
                controllerInstance.freshData = False
                print('data logged succesfully')
                return True
            # if no wifi, try again later
            except requests.exceptions.ConnectionError:
                print('no WiFi right now')
                time.sleep(wifiCheckTime)
    else:
        print('no data to log!')
