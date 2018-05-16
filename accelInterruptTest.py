# accelInterruptTest.py
# CRT
# created 5/16/2018
# last updated 5/16/2018
# tests the accelerometer/GPIO interrupts

import accelSensor
import RPi.GPIO as GPIO

# mode: pin number
GPIO.setmode(GPIO.BOARD)

actPin = 29
inactPin = 31

GPIO.setwarnings(False)
GPIO.setup([actPin, inactPin], GPIO.IN)

def actDetected():
    print('activity detected!')

def inactDetected():
    print('inactivity detected!')

GPIO.add_event_detect(actPin, GPIO.RISING, actDetected)
GPIO.add_event_detect(inactPin, GPIO.RISING, inactDetected)

print('GPIO interrupts ready')

while True:
    time.sleep(30)
