import RPi.GPIO as GPIO
import sys
import time

GPIO.setmode(GPIO.BCM)


servo_pin = 18
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)

#pwm.start(0.0)



def arm_up():
	pwm.start(0)
	pwm.ChangeDutyCycle(10)
	time.sleep(1)
	pwm.stop(0)
	
def arm_down():
	pwm.start(0)
	pwm.ChangeDutyCycle(2.5)
	time.sleep(1)
	pwm.stop(0)


arm_up() # test
GPIO.cleanup()
