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
import binascii

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

        xTwos = self.twosComp(xBits, self.numDataBits)
        yTwos = self.twosComp(yBits, self.numDataBits)
        zTwos = self.twosComp(zBits, self.numDataBits)

        xVal = self.lsbToMPS * float(xTwos)
        yVal = self.lsbToMPS * float(yTwos)
        zVal = self.lsbToMPS * float(zTwos)

        return (xVal, yVal, zVal)

    # get the value represented by a twos-complement number
    def twosComp(self, num, numBits):
        msb = num & (1 << (numBits-1))
        return num - (2 * msb)

    def __init__(self):
        # set up SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        # CPHA = CPOL = 0
        self.spi.mode = 0b00
        # recommended speeds 1MHz - 8MHz
        self.spi.max_speed_hz = 1000000

        # these data are 12-bit but twos-complement uses sign extension
        # so for all intents and purposes it is 16-bit
        self.numDataBits = 16

        self.lsbToMPS = 0.0098

        # make sure the device reset properly
        if not (self.spiRead(REG_STATUS, 1) == 0x40):
            print('ADXL362 did not start up correctly')

        # start measurement mode
        self.spiWrite(REG_POWER_CTL, [VAL_MEAS_NORM])

adxl = AccelSensor()
while True:
    print(adxl.readXYZ())
    time.sleep(1)
