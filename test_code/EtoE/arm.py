import RPi.GPIO as GPIO
import sys
import time

# 2.5 ~ 12

class Arm():
	def __init__(self,servo_pin):
		self.servo_pin = servo_pin
		
	def setup(self):
		GPIO.setmode(GPIO.BCM)
		self.mode = GPIO.getmode()
		# print(mode)
		GPIO.setup(self.servo_pin, GPIO.OUT)
		self.pwm = GPIO.PWM(self.servo_pin, 50) #電圧を参照するピンを周波数50HZに指定
		self.pwm.start(0)

	def up(self,buff=0):
		self.pwm.ChangeDutyCycle(5.5+buff)
	
	def down(self,buff=0):
		self.pwm.ChangeDutyCycle(2.5+buff)

	def move(self,ref):
		self.pwm.ChangeDutyCycle(ref)
		
	def stop(self):
		self.pwm.stop(0)

	def calibration(self):
		return
