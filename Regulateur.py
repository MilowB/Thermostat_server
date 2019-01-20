from threading import Thread
import RPi.GPIO as GPIO

class Regulateur(Thread):

    """Thread chargé simplement d'afficher une lettre dans la console."""

    def __init__(self, thermostat):
        Thread.__init__(self)
        self.thermostat = thermostat

    def run(self):
        print("Thread Regulator is running") #debug
        GPIO.setmode(GPIO.BCM)
        time_sleep = 5 #5 * 60
        cpt = 0
        while True:
            thermostat.updateData()
            if thermostat.needHeating():
                GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
            else:
                GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)
            # Would be better to the SD card to check every 5 * 60 seconds
            time.sleep(time_sleep)
            # Write data every hours to prevent the degradation of the SD card
            if cpt % 12 == 0:
                thermostat.saveData()
            cpt += 1