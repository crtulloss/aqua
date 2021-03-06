# accelSensor.py
# CRT
# created 5/15/2018
# last updated 5/16/2018
# provides functions to get accelerometer data

# get gpio readings
# set up accelerometer interrupts
# wait for the activity interrupt on that pin and have it print something

import spidev
import time
import logging

import utility

# commands
COMMAND_WRITE = 0x0A
COMMAND_READ = 0x0B
COMMAND_READ_FIFO = 0x0D

# registers
REG_STATUS = 0x0B
REG_X_L = 0x0E
REG_X_H = 0x0F
REG_Y_L = 0x10
REG_Y_H = 0x11
REG_Z_L = 0x12
REG_Z_H = 0x13
REG_TEMP_L = 0x14
REG_TEMP_H = 0x15
REG_SOFT_RESET = 0x1F
REG_THRESH_ACT_L = 0x20
REG_THRESH_ACT_H = 0x21
REG_TIME_ACT = 0x22
REG_ACT_INACT_CTL = 0x27
REG_INTMAP1 = 0x2A
REG_INTMAP2 = 0x2B
REG_POWER_CTL = 0x2D

# values for register writes
VAL_MEAS_NORM = 0x02
VAL_MEAS_AUTOSLEEP = 0x06
VAL_MEAS_AS_WU = 0x0E
VAL_ACTINACT_LOOP = 0x3F
VAL_ACTINACT_DEFAULT = 0x0F
VAL_INT_ACT = 0x10
VAL_INT_INACT = 0x20
VAL_INT_AWAKE = 0x40
VAL_SOFT_RESET = 0x52

# these data are 12-bit but twos-complement uses sign extension
# so for all intents and purposes it is 16-bit
numDataBits = 16

lsbToMPSS = 0.0098

# activity and inactivity thresholds in mg - these are sample values
# from datasheet
activityThreshBytes = 250
activityThreshHigh = (int(activityThreshBytes) & 0xFF00) >> 8
activityThreshLow = int(activityThreshBytes) & 0x00FF

inactivityThreshBytes = 150
inactivityThreshHigh = (int(inactivityThreshBytes) & 0xFF00) >> 8
inactivityThreshLow = int(inactivityThreshBytes) & 0x00FF

# activity and inactivity times
actTime = 0.5
inactTime = 20.0
# default data rate
odr = 100.0
actNumSamples = int(actTime * odr)
if (actNumSamples > 0xFF):
    actNumSample = 0xFF
inactNumSamples = int(inactTime * odr)
if (inactNumSamples > 0xFFFF):
    inactNumSample = 0xFFFF
inactNumSamplesHigh = (inactNumSamples & 0xFF00) >> 8
inactNumSamplesLow = inactNumSamples & 0x00FF

# ADXL362 class, which is used to send SPI commands to the ADXL362 chip
class AccelSensor(object):

    # read some number of bytes starting at the specified register
    def spiRead(self, firstAddress, numBytes):
        bytesToTransfer = [COMMAND_READ, firstAddress]
        for n in range(numBytes):
            bytesToTransfer.append(0x00)
        response = self.spi.xfer2(bytesToTransfer)
        return response[2:]

    # write some bytes starting at the specified register
    def spiWrite(self, firstAddress, bytesToWrite):
        bytesToTransfer = [COMMAND_WRITE, firstAddress]
        for b in bytesToWrite:
            bytesToTransfer.append(b)
        response = self.spi.xfer2(bytesToTransfer)
        return response[2:]

    # read XYZ data
    def readXYZ(self):
        data = self.spiRead(REG_X_L, 6)
        xBits = (data[0] + (data[1] << 8))
        yBits = (data[2] + (data[3] << 8))
        zBits = (data[4] + (data[5] << 8))

        xTwos = self.twosComp(xBits, numDataBits)
        yTwos = self.twosComp(yBits, numDataBits)
        zTwos = self.twosComp(zBits, numDataBits)

        xVal = lsbToMPSS * float(xTwos)
        yVal = lsbToMPSS * float(yTwos)
        zVal = lsbToMPSS * float(zTwos)

        return (xVal, yVal, zVal)

    # get the value represented by a twos-complement number
    def twosComp(self, num, numBits):
        msb = num & (1 << (numBits-1))
        return num - (2 * msb)

    # set up operation for loop mode with activity and inactivity interrupts
    # determined by the motion and time thesholds set above
    # order is critical here. interrupt settings -> interrupt pin map ->
    # power control
    def setupInterrupts(self):
        # set activity and inactivity thresholds, times, loop mode, and reference mode (not absolute)
        interruptSettings = [activityThreshLow, activityThreshHigh, actNumSamples, inactivityThreshLow, inactivityThreshHigh, inactNumSamplesLow, inactNumSamplesHigh, VAL_ACTINACT_LOOP]
        self.spiWrite(REG_THRESH_ACT_L, interruptSettings)
        # map the ACT -> INT1, INACT -> INT2
        self.spiWrite(REG_INTMAP1, [VAL_INT_ACT, VAL_INT_INACT])
        # go into autosleep mode
        self.spiWrite(REG_POWER_CTL, [VAL_MEAS_AUTOSLEEP])

    def clearInterrupts(self):
        return self.spiRead(REG_STATUS, 1)

    def __init__(self):
        utility.printAndLog('setting up accelerometer SPI')
        # set up SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        # CPHA = CPOL = 0
        self.spi.mode = 0b00
        # recommended speeds 1MHz - 8MHz
        self.spi.max_speed_hz = 1000000
        # soft reset
        utility.printAndLog('accel soft reset')
        self.spiWrite(REG_SOFT_RESET, [VAL_SOFT_RESET])
        time.sleep(0.5)
        # setup interrupts and mode
        utility.printAndLog('setting up accel interrupts')
        self.setupInterrupts()
