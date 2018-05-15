# fonagpsSheetLogger.py
# CRT
# created 5/9/2018
# last modified 5/9/2018

# modified from InitialState data logger fonagps.py

from os import system
import serial
import subprocess
from time import sleep
import requests

SECONDS_BETWEEN_READS = 10

# WebApp info
publicURL = "https://script.google.com/macros/s/AKfycbxKm2AWyX6unin8LXDkbL7l1SUre2bDJNTTGUyMk9VhXmJRgMs/exec"
sheetName = "sophonTests"
pointsPerLog = 4

# GPS interaction strings
gpsCheck = "AT+CGNSINF\r"

# Start PPPD
def openPPPD():
	# Check if PPPD is already running by looking at syslog output
	output1 = str(subprocess.check_output("cat /var/log/syslog | grep pppd | tail -1", shell=True))
	if(("secondary DNS address" not in output1) and ("locked" not in output1)):
		while True:
			# Start the "fona" process
			subprocess.call("sudo pon fona", shell=True)
			sleep(2)
			output2 = str(subprocess.check_output("cat /var/log/syslog | grep pppd | tail -1", shell=True))
			if ("script failed" not in output2):
				break
	# Make sure the connection is working
	while True:
		output2 = str(subprocess.check_output("cat /var/log/syslog | grep pppd | tail -1", shell=True))
		output3 = str(subprocess.check_output("cat /var/log/syslog | grep pppd | tail -3", shell=True))
		if (("secondary DNS address" in output2) or ("secondary DNS address" in output3)):
			return True

# Stop PPPD
def closePPPD():
	print("turning off cell connection")
	# Stop the "fona" process
	subprocess.call("sudo poff fona", shell=True)
	# Make sure connection was actually terminated
	while True:
		output = str(subprocess.check_output("cat /var/log/syslog | grep pppd | tail -1", shell=True))
		if ("Exit" in output):
			return True

# Check for a GPS fix
def checkForFix():
	print("checking for fix")
	# Start the serial connection
	ser=serial.Serial('/dev/serial0', 115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
	# Turn on the GPS
	powerOn = "AT+CGNSPWR=1\r"
	powerCheck = "AT+CGNSPWR?\r"
	ser.write(powerOn.encode())
	ser.write(powerCheck.encode())
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
				print("fix found")
				print(response)
				return True
			# If a fix wasn't found, wait and try again
			if ("+CGNSINF: 1,0," in response):
				sleep(5)
				ser.write(gpsCheck.encode())
				print("still looking for fix")
			else:
				#print "something else went wrong"
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
			print("Latitude: %s" % lat)
			lon = array[4]
			print("Longitude: %s\n" % lon)
			return (lat,lon)

# things to modify for AQUA:
# instead of flush, could either use web app, or I could set up a separate script to
# upload the data when connected to WIFI

# Start the program by opening the cellular connection and creating a bucket for our data
def getAndLogData():
	print("starting GPS data collection and logging script")
	if openPPPD():
		# Wait long enough for the request to complete
		sleep(10)
	
		print("conection tested succesfully")

		while True:
			# Close the cellular connection
			if closePPPD():
				print("closing connection")
				sleep(1)
		
			# empty lists for the data to be collected
			latList = []
			longList = []

			for i in range(pointsPerLog):
				# Make sure there's a GPS fix
				if checkForFix():
					# Get lat and long
					if getCoord():
						latitude, longitude = getCoord()
						# Store the coordinates
						latList.append(latitude)
						longList.append(longitude)
						sleep(SECONDS_BETWEEN_READS)
				# Turn the cellular connection on every 10 reads
				if i == (pointsPerLog-1):
					print("opening connection")

					if openPPPD():
						print("logging data to sheet")
						# log data to sheet
						for j in range(pointsPerLog):
							thisLat = latList[j]
							thisLong = longList[j]
							data = {'sheet':sheetName,'Latitude':thisLat, 'Longitude':thisLong}
							requests.get(publicURL, params=data)
						print("logging complete")
