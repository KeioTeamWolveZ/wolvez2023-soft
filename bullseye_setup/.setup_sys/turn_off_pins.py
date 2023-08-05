import RPi.GPIO as GPIO
import time

pin1 = 25
pin2 = 24
pin3 = 17

GPIO.setmode(GPIO.BCM)

for pin in [pin1,pin2,pin3]:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,0)
    print(f'pin {pin} turned off')

GPIO.cleanup()
