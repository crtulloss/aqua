# BicycleController.py
# CRT
# created 5/13/2018
# last updated 5/13/2018
# defines the BicycleController class to manage the controller state machine

from transitions import Machine
import time
import aquaGPS
import darknessSensor
import illuminator
import misc

# Controller class, which inherits the Machine class
class BicycleController(Machine):

    timeBetweenGPSReads = 30
    timeBetweenAccelReads = 5
    accelReadsBetweenGPS = timeBetweenGPSReads / timeBetweenAccelReads

    # STATE CALLBACKS
    # on_enter callback for nap
    def housekeep(self):
        print('housekeeping')
        illuminator.turnLightsOff()
        #turnGPSOff()
        misc.checkWiFi()

    # on_enter callback for commute
    def monitorSensors(self):
        print('monitoring sensors')
        # check darkness and adjust LEDs appropriately
        if (darknessSensor.isDark()):
            illuminator.lightsOn()
        else:
            illuminator.lightsOff()
        # location check
        # get GPS coordinates
        (lat,lon) = aquaGPS.getCoord()
        # check if we are home - if so, wait 30 seconds then try to nap
        if (aquaGPS.homeZone()):
            sleep(30)
            # this transition will fail if still moving
            if not self.slumber():
                # continue monitoring
                self.monitorSensors()
        # if not, begin a ride
        else:
            self.there()

    # on_enter callback for ride
    def collectData(self):
        print('beginning ride')
        # check darkness and adjust LEDs appropriately
        if (darknessSensor.isDark()):
            illuminator.lightsOn()
        else:
            illuminator.lightsOff()
        # check previous state - if commute, make new data file
        if (self.previous == commute):
            self.accelFileName = misc.makeFileName('accel')
            self.gpsFileName = misc.makeFileName('gps')
        # otherwise, use the one that already exists
        else:
            misc.writeToFile(self.accelFileName, self.accelDataBuffer)
            self.accelDataBuffer = ''
        # main data collection: accelerometer
        for reading in range(accelReadsBetweenGPS):
            # get accelerometer data and store in file
            (x,y,z,temp) = accel.read_xyz()
            t = misc.makeTimeStamp()
            accelData = '%s\t%s\t%s\t%s\n' % (t, x, y, z)
            misc.writeToFile(self.accelFileName, accelData)
            # sleep
            sleep(timeBetweenAccelReads)
        # location check
        # get GPS coordinates
        (lat,lon) = aquaGPS.getCoord()
        t = misc.makeTimeStamp()
        # log GPS data
        gpsData = '%s\t%s\t%s\n' % (t, lat, lon)
        misc.writeToFile(self.gpsFileName, gpsData)
        # check if we are home - if so, transition to commute
        if (aquaGPS.homeZone()):
            self.back_again()
        # if not, continue to log data
        else:
            self.collectData()

    # on_exit callback for all states: sets the previous state to the
    # current one as we leave it
    def setPrevious(self):
        self.previous = self.state
        return self.previous

    # CONDITONS
    # condition for commute -> nap transition
    def notMoving(self):
        return True

    # STATES
    nap = {'name':'nap', 'on_enter':['housekeep'], 'on_exit':['setPrevious']}
    commute = {'name':'commute', 'on_enter':['monitorSensors'], 'on_exit':['setPrevious']}
    ride = {'name':'ride', 'on_enter':['collectData'], 'on_exit':['setPrevious']}

    states = [nap, commute, ride]

    def __init__(self):

        Machine.__init__(self, states=BicycleController.states, initial='nap')

        self.previous = self.state
        self.accelFileName = ''
        self.gpsFileName = ''
        self.accelDataBuffer = ''

        self.add_transition('awaken', 'nap', 'commute')
        self.add_transition('slumber', 'commute', 'nap', conditions=['notMoving'])
        self.add_transition('there', 'commute', 'ride')
        self.add_transition('back_again', 'ride', 'commute')
