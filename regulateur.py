import time
import RPi.GPIO as GPIO
from Thermostat import *

def main():
    GPIO.setmode(GPIO.BCM)
    thermostat = Thermostat()
    while True:
        thermostat.updateData()
        if thermostat.needHeating():
            GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
        else:
            GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH)

        time.sleep(2)

if __name__ == '__main__':
   main()