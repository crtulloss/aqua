# illuminator.py
# CRT
# created 5/14/2018
# last updated 5/14/2018
# provides functions to turn on/off/blink right and left LEDs
import RPi.GPIO as GPIO
import time

# LED pins
leftLights = 18
rightLights = 16

# morse code definition
unit = 0.2
dot = unit
dash = 3.0 * unit
C = [dash, dot, dash, dot]
R = [dot, dash, dot]
T = [dash]
signoffSeq = [C,R,T]

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

# when going inactive, sign my initials so I know it's working
def signoff():
    lightsOff()
    for letter in signoffSeq:
        for part in letter:
            lightsOn()
            time.sleep(unit)
            lightsOff()
            time.sleep(unit)
        time.sleep(dash - unit)
