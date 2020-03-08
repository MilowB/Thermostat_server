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
        self.thermostat.updateData()
        if self.thermostat.needHeating():
            GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
            self.thermostat.heating = True
        else:
            GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)
            self.thermostat.heating = False

    def run(self):
        time_sleep = 5 * 60
        while True:
            self.update()
            time.sleep(time_sleep)