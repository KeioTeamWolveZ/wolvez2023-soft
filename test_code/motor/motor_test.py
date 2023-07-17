import time
import RPi.GPIO as GPIO
import motor
GPIO.setwarnings(False)

MotorR = motor.motor(6,5,13)
MotorL = motor.motor(20,16,12)

try:
	print("\nRUN\n")
	MotorR.go(70)
	MotorL.go(70)
	
	time.sleep(1)
	
	print("\nSTOP\n")
	MotorR.stop()
	MotorL.stop()
	time.sleep(1)
except KeyboardInterrupt:
	MotorR.stop()
	MotorL.stop()
	time.sleep(1)
	GPIO.cleanup()
	
GPIO.cleanup()
