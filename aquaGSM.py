# aquaGPS.py
# CRT
# created 5/9/2018
# last updated 5/14/2018

import serial
import subprocess
from time import sleep

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
		print(output)
		if ("Exit" in output):
			return True
