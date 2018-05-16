# accelSensor.py
# CRT
# created 5/15/2018
# last updated 5/15/2018
# provides functions to get accelerometer data

# get gpio readings
# set up accelerometer interrupts
# wait for the activity interrupt on that pin and have it print something

import spidev
import time

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
VAL_ACTINACT_LOOP = 0x3F
VAL_INT_ACT = 0x10
VAL_INT_INACT = 0x20

# these data are 12-bit but twos-complement uses sign extension
# so for all intents and purposes it is 16-bit
numDataBits = 16

lsbToMPSS = 0.0098

# activity and inactivity thresholds in m/s^2
activityThresh = 0.1
activityThreshBytes = activityThresh / lsbToMPSS
int(activityThreshBytes)
activityThreshHigh = int(activityThreshBytes) & 0xFF00
activityThreshLow = int(activityThreshBytes) & 0x00FF

inactivityThresh = 0.1
inactivityThreshBytes = inactivityThresh / lsbToMPSS
int(inactivityThreshBytes)
inactivityThreshHigh = int(inactivityThreshBytes) & 0xFF00
inactivityThreshLow = int(inactivityThreshBytes) & 0x00FF

# activity and inactivity times
actTime = 1.0
inactTime = 60.0
# default data rate
odr = 100
actNumSamples = int(actTime * odr)
if (actNumSamples > 0xFF):
    actNumSample = 0xFF
inactNumSamples = int(inactTime * odr)
if (inactNumSamples > 0xFF):
    inactNumSample = 0xFF
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

    def setupInterrupts(self):
        # set activity and inactivity thresholds, times, loop mode, and reference mode (not absolute)
        self.spiWrite(REG_THRESH_ACT_L, [activityThreshLow, activityThreshHigh, 1, inactivityThreshLow, inactivityThreshHigh, 1, VAL_ACTINACT_LOOP])
        print(self.spiRead(REG_THRESH_ACT_L, 7))
        # map the ACT -> INT1, INACT -> INT2
        self.spiWrite(REG_INTMAP1, [VAL_INT_ACT, VAL_INT_INACT])
        print(self.spiRead(REG_INTMAP1, 2))
        # go into autosleep mode
        self.spiWrite(REG_POWER_CTL, [VAL_MEAS_AUTOSLEEP])
        print(self.spiRead(REG_POWER_CTL, 1))

    def readStatusReg(self):
        return self.spiRead(REG_STATUS, 1)

    def __init__(self):
        print('setting up accelerometer SPI')
        # set up SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        # CPHA = CPOL = 0
        self.spi.mode = 0b00
        # recommended speeds 1MHz - 8MHz
        self.spi.max_speed_hz = 1000000

        # start measurement mode
        print('beginning accel measurement mode')
        self.spiWrite(REG_POWER_CTL, [VAL_MEAS_NORM])

        # setup interrupts
        print('setting up accel interrupts')
        self.setupInterrupts()

# the actual instance used for state machine transitions and data collection
adxl = AccelSensor()

def getXYZData():
    return adxl.readXYZ()

def clearInterrupts():
    return adxl.readStatusReg()
