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
import logging

# my code
from bicycleController import BicycleController
from accelSensor import AccelSensor
import aquaGPS
import darknessSensor
import illuminator
import dataLogger

# logging setup
# for the debugging level, info messages will be logged, along with errors
logging.basicConfig(filename='daemonicLogs.log', level=logging.DEBUG)

# daemons need to rest
lurkDowntime = 30

# GPIO setup
# mode: pin number
GPIO.setmode(GPIO.BOARD)
# accelerometer interrupts
actPin = 29
inactPin = 31
# turn buttons
leftTurn = 15
rightTurn = 13

GPIO.setwarnings(False)
GPIO.setup([actPin, inactPin, leftTurn, rightTurn], GPIO.IN)
GPIO.setup([illuminator.leftLights, illuminator.rightLights], GPIO.OUT)

requests.get(dataLogger.publicURL, params={'sheet':'aqua daemon tests', 'Status': 'ALIVE'})

# setup accelerometer (including interrupts)
adxl = AccelSensor()

# setup controller
aqC = BicycleController(adxl)

# hello
illuminator.sign()

# the normal behavior of a daemon is to lurk
def lurk():
    logging.info('lurking for %d seconds' % lurkDowntime)
    time.sleep(lurkDowntime)
    if (aqC.state == 'nap'):
        pass
    elif (aqC.state == 'commute'):
        aqC.monitorSensors()

# setup accelerometer interrupts - state machine transitions
def actDetected(pin):
    logging.info('activity detected!')
    if (aqC.state == 'nap'):
        aqC.awaken()

def inactDetected(pin):
    logging.info('inactivity detected!')
    if (aqC.state == 'commute'):
        aqC.slumber()

# choose whether to turn lights on or off
def doLights():
    if (darknessSensor.isDark()):
        illuminator.lightsOn()
    else:
        illuminator.lightsOff()

# turn interrupts
def turnButton(pin):
    # not enabled during naps
    if not (aqC.state == 'nap'):
        if (pin == leftTurn):
            # if already in a turn, finish the turn
            # could end up back in this interrupt, but that's ok
            # because the last thing that will happen is always
            # regular old doLights()
            if (aqC.turningLeft):
                aqC.turningLeft = False
            else:
                # othewise, blink the lights until turn is complete
                while (aqC.turningLeft):
                    illuminator.blinkLeft()
        else:
            if (aqC.turningRight):
                aqC.turningRight = False
            else:
                while (aqC.turningLeft):
                    illuminator.blinkLeft()
        doLights()

GPIO.add_event_detect(actPin, GPIO.RISING, actDetected)
GPIO.add_event_detect(inactPin, GPIO.RISING, inactDetected)
GPIO.add_event_detect(leftTurn, GPIO.RISING, turnButton)
GPIO.add_event_detect(rightTurn, GPIO.RISING, turnButton)
logging.info('GPIO interrupts ready')
time.sleep(5)
logging.info('clearing accel status register')
adxl.clearInterrupts()

# lurk patiently in the background, forever....
while True:
    lurk()
