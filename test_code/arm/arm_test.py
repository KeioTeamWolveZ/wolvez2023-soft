import RPi.GPIO as GPIO
import sys
import time

GPIO.setmode(GPIO.BCM)

mode = GPIO.getmode()
print(mode)

servo_pin = 23
GPIO.setup(servo_pin, GPIO.OUT)

pwm = GPIO.PWM(servo_pin, 50)

#pwm.start(0.0)

pwm.start(0)
while True:
	try:
		pwm.ChangeDutyCycle(5.5)
		time.sleep(1)
		pwm.ChangeDutyCycle(2.5)
		time.sleep(5)
	except KeyboardInterrupt:
		pwm.stop(0)
		GPIO.cleanup()
		break

pwm.stop(0)
GPIO.cleanup()
