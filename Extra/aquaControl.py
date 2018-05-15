# aquaControl.py
# CRT
# last updated 5/9/2018

import requests
import triggeredGPS
from time import sleep

# magic numbers
LATITUDE_THRESHOLD = 41.83
GPS_CHECK_PERIOD = 60

while True:
	fixFound = triggeredGPS.checkForFix()
	if (fixFound):
		(currentLat, currentLong) = triggeredGPS.getCoord()

		if (float(currentLat) < LATITUDE_THRESHOLD):
			print("beginning ride")
			triggeredGPS.getAndLogData(LATITUDE_THRESHOLD)
		else:
			print("threshold not reached")
	else:
		print("no GPS signal")
	sleep(GPS_CHECK_PERIOD)
