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
import utility

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
endTurn = 13
rightTurn = 11

GPIO.setwarnings(False)
GPIO.setup([actPin, inactPin, leftTurn, rightTurn, endTurn], GPIO.IN)
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
    utility.printAndLog('lurking for %d seconds' % lurkDowntime)
    time.sleep(lurkDowntime)
    if (aqC.state == 'nap'):
        pass
    elif (aqC.state == 'commute'):
        aqC.monitorSensors()

# setup accelerometer interrupts - state machine transitions
def actDetected(pin):
    utility.printAndLog('activity detected!')
    if (aqC.state == 'nap'):
        aqC.awaken()

def inactDetected(pin):
    utility.printAndLog('inactivity detected!')
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
    if (aqC.state == 'commute'):
        if (pin == leftTurn):
            # begin turn
            utility.printAndLog('beginning left turn')
            aqC.turningLeft = True
            while (aqC.turningLeft):
                # blink and check for the signal to stop
                illuminator.blinkLeft()
                if (GPIO.input(endTurn)):
                    print('ending turn')
                    aqC.turningLeft = False
                    doLights()
                    return
        else:
            # begin turn
            utility.printAndLog('beginning right turn')
            aqC.turningRight = True
            while (aqC.turningRight):
                # blink and check for the signal to stop
                illuminator.blinkRight()
                if (GPIO.input(endTurn)):
                    print('ending turn')
                    aqC.turningRight = False
                    doLights()
                    return

GPIO.add_event_detect(actPin, GPIO.RISING, actDetected)
GPIO.add_event_detect(inactPin, GPIO.RISING, inactDetected)
GPIO.add_event_detect(leftTurn, GPIO.RISING, turnButton, bouncetime=1000)
GPIO.add_event_detect(rightTurn, GPIO.RISING, turnButton, bouncetime=1000)
utility.printAndLog('GPIO interrupts ready')
time.sleep(5)
utility.printAndLog('clearing accel status register')
adxl.clearInterrupts()

# lurk patiently in the background, forever....
while True:
    lurk()
