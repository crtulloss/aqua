#!/usr/bin/env python3

# aqua.py
# CRT
# created 5/12/2018
# last updated 5/12/2018

import requests
from time import sleep
from transitions import Machine

publicURL = 'https://script.google.com/macros/s/AKfycbxKm2AWyX6unin8LXDkbL7l1SUre2bDJNTTGUyMk9VhXmJRgMs/exec'
sheetName = 'aqua daemon tests'

while True:
	data = {'sheet':sheetName, 'Status':'ALIVE'}
#	requests.get(publicURL, params=data)
	sleep(30)
