import RPI.GPIO as GPIO
import time

pin1 = 25
pin2 = 24
pin3 = 8

GPIO.setmode(BCM)

for pin in [pin1,pin2,pin3]:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,0)

GPIO.cleanup()
