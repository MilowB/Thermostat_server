import time
import RPi.GPIO as GPIO
from Thermostat import *

def main():
    GPIO.setmode(GPIO.BCM)
    thermostat = Thermostat()
    time_sleep = 5 * 60
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

if __name__ == '__main__':
   main()