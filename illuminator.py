# illuminator.py
# CRT
# created 5/14/2018
# last updated 5/14/2018
# provides functions to turn on/off/blink right and left LEDs
import RPi.GPIO as GPIO
import time

# LEDs
leftLights = 18
rightLights = 16
# turn buttons
leftTurn = 15
rightTurn = 13

# pretty self-explanatory
def lightsOff():
    GPIO.output(leftLights, GPIO.LOW)
    GPIO.output(rightLights, GPIO.LOW)

def lightsOn():
    GPIO.output(leftLights, GPIO.HIGH)
    GPIO.output(rightLights, GPIO.HIGH)

# start with a low transition because these are most important at night,
# when the lights will be on at first
def blinkRight():
    GPIO.output(rightLights, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(rightLights, GPIO.HIGH)
    time.sleep(0.5)

def blinkLeft():
    GPIO.output(leftLights, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(leftLights, GPIO.HIGH)
    time.sleep(0.5)
