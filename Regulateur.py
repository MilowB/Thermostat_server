from threading import Thread
import RPi.GPIO as GPIO
import time

class Regulateur(Thread):
    def __init__(self, thermostat):
        Thread.__init__(self)
        self.thermostat = thermostat
        self.updating = False
        GPIO.setmode(GPIO.BCM)

    def update(self):
        #time_sleep = 4 * 60
        #while True:
        self.thermostat.updateData()
        if self.thermostat.needHeating():
            GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
            self.thermostat.heating = True
        else:
            GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)
            self.thermostat.heating = False
            # Would be better for the SD card to check every 5 * 60 seconds
            #time.sleep(time_sleep)
            # Write data every hours to prevent the degradation of the SD card
            #if cpt % 12 == 0:
            #    self.thermostat.saveData()
            #cpt += 1