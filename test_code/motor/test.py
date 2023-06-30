import motor
import RPi.GPIO as GPIO
import time 
from datetime import datetime

Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

Motor1.go(70)
Motor2.go(70)
time.sleep(3)
Motor1.stop()
Motor2.stop()
GPIO.cleanup()
