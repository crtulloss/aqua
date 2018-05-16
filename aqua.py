#!/usr/bin/env python3

# aqua.py
# CRT
# created 5/12/2018
# last updated 5/16/2018
# daemon for bike control - includes controller and accelerometer instances

# other packages
import requests
from transitions import Machine
import RPi.GPIO as GPIO
import time
import serial
import tsl2591

# my code
from bicycleController import BicycleController
from accelSensor import AccelSensor
import aquaGPS
import darknessSensor
import illuminator
import misc

# data logging spreadsheet settings
publicURL = 'https://script.google.com/macros/s/AKfycbxKm2AWyX6unin8LXDkbL7l1SUre2bDJNTTGUyMk9VhXmJRgMs/exec'
sheetName = 'aqua state machine tests'

# daemons need to rest
lurkDowntime = 30

# GPIO setup
# mode: pin number
GPIO.setmode(GPIO.BOARD)
actPin = 29
inactPin = 31
GPIO.setwarnings(False)
GPIO.setup([actPin, inactPin], GPIO.IN)

# setup accelerometer (including interrupts)
adxl = AccelSensor()

# setup controller
aqC = BicycleController(adxl)

# the normal behavior of a daemon is to lurk
def lurk():
    print('lurking for %d seconds' % lurkDowntime)
    time.sleep(lurkDowntime)
    if (aqC.state == 'nap'):
        pass
    elif (aqC.state == 'commute'):
        aqC.monitorSensors()

# setup accelerometer interrupts - state machine transitions
def actDetected(pin):
    print('activity detected!')
    if (aqC.state == 'nap'):
        aqC.awaken()

def inactDetected(pin):
    print('inactivity detected!')
    if (aqC.state == 'commute'):
        aqC.slumber()

GPIO.add_event_detect(actPin, GPIO.RISING, actDetected)
GPIO.add_event_detect(inactPin, GPIO.RISING, inactDetected)
print('GPIO interrupts ready')
time.sleep(5)
print('clearing accel status register')
adxl.clearInterrupts()

# lurk patiently in the background, forever....
while True:
    lurk()
