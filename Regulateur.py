from threading import Thread
import RPi.GPIO as GPIO
import time

class Regulateur(Thread):

    """Thread chargé simplement d'afficher une lettre dans la console."""

    def __init__(self, thermostat):
        Thread.__init__(self)
        self.thermostat = thermostat

    def run(self):
        print("Thread Regulator is running") #debug
        GPIO.setmode(GPIO.BCM)
        time_sleep = 30 #5 * 60
        cpt = 0
        while True:
            self.thermostat.updateData()
            if self.thermostat.needHeating():
                GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
                thermostat.heating = True
            else:
                GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)
                thermostat.heating = False
            # Would be better to the SD card to check every 5 * 60 seconds
            time.sleep(time_sleep)
            # Write data every hours to prevent the degradation of the SD card
            if cpt % 12 == 0:
                self.thermostat.saveData()
            cpt += 1