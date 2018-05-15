# darknessSensor.py
# CRT
# created 5/15/2018
# last updated 5/15/2018
# provides functions to assess the light level,
# using maxlklaxl's TSL2591 smbus python package

# installation procedure was weird, so there is a read_tsl.py function
# that accomplishes the same thing, but this package is actually installed on
# RPi
# also note that it won't work on a PC because we don't have access to smbus
import tsl2591
from time import sleep

# darkness threshold
darknessThreshold = 50.0

# create the dude
aquaTSL2591 = tsl2591.Tsl2591()

def isDark():
    # query the full and IR-only light values
    full,ir = aquaTSL2591.get_full_luminosity()
    # convert to lux
    lux = aquaTSL2591.calculate_lux(full,ir)
    # compare against threshold
    if (lux < darknessThreshold):
        print("it's dark!")
        return True
    else:
        print("it's light!")
        return False
