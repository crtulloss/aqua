# controllerTest.py
# CRT
# created 5/15/2018
# last updated 5/15/2018
# manual test of the BicycleController state machine

from transitions import Machine
import time
import aquaGPS
import darknessSensor
import illuminator
import misc
import bicycleController

bc = bicycleController.BicycleController()

print(bc.state)
print(bc.awaken())
print(bc.state)
