# aquaGPS.py
# CRT
# created 5/9/2018
# last updated 5/14/2018

# modified from InitialState data logger fonagps.py

import serial
from time import sleep
import logging

import utility

# GPS interaction strings
gpsCheck = "AT+CGNSINF\r"
gpsPowerCheck = "AT+CGNSPWR?\r"
gpsPowerOn = "AT+CGNSPWR=1\r"
gpsPowerOff = "AT+CGNSPWR=0\r"

homeNorth = 41.8357		# olney street
homeSouth = 41.8226		# williams street

homeEast = -71.3904		# gano street
homeWest = -71.4077		# benefit (curves) and angell

# close boundaries around brick house, for testing
# homeNorth = 41.8293
# homeSouth = 41.8285
#
# homeWest = -71.3940
# homeEast = -71.3932

# Check for a GPS fix
def checkForFix():
	utility.printAndLog("checking for fix")
	# Start the serial connection
	ser=serial.Serial('/dev/serial0', 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
	# Turn on the GPS
	ser.write(gpsPowerOn.encode())
	ser.write(gpsPowerCheck.encode())
	while True:
		response = str(ser.readline())
		if (" 1" in response):
			break
	# Ask for the navigation info parsed from NMEA sentences
	ser.write(gpsCheck.encode())
	while True:
			response = str(ser.readline())
			# Check if a fix was found
			if ("+CGNSINF: 1,1," in response):
				utility.printAndLog("fix found")
				return True
			# If a fix wasn't found, wait and try again
			if ("+CGNSINF: 1,0," in response):
				sleep(5)
				ser.write(gpsCheck.encode())
				utility.printAndLog("still looking for fix")
				# turn the GPS off to save power
				ser.write(gpsPowerOff.encode())
				return False
			else:
				# still waiting for response
				ser.write(gpsCheck.encode())

# Read the GPS data for Latitude and Longitude
def getCoord():
	# Start the serial connection
	ser=serial.Serial('/dev/serial0', 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
	ser.write(gpsCheck.encode())
	while True:
		response = str(ser.readline())
		if ("+CGNSINF: 1," in response):
			# Split the reading by commas and return the parts referencing lat and long
			array = response.split(",")
			lat = array[3]
			utility.printAndLog("Latitude: %s" % lat)
			lon = array[4]
			utility.printAndLog("Longitude: %s\n" % lon)
			# turn GPS off
			ser.write(gpsPowerOff.encode())
			return (lat,lon)

# figure out if we are in home zone or not - GPS thresholds defined above
def homeZone(lat, lon):
	# convert strings to floats
	if type(lat) == str:
		lat = float(lat)
	if type(lon) == str:
		lon = float(lon)
	if (lat > homeNorth) | (lat < homeSouth) | (lon > homeEast) | (lon < homeWest):
		return False
	else:
		return True
