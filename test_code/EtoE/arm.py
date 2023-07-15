import RPi.GPIO as GPIO
import pigpio as pg
#import wiringpi as wp
import sys
import time

# 

class Arm():
	def __init__(self,servo_pin):
		self.servo_pin = servo_pin
		
	def setup(self):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		self.mode = GPIO.getmode()
		# print(mode)
		GPIO.setup(self.servo_pin, GPIO.OUT)
		self.pwm = GPIO.PWM(self.servo_pin, 50) #電圧を参照するピンを周波数50HZに指定
		self.pwm.start(0)

	def up(self,buff=0):
		GPIO.output(self.servo_pin,GPIO.HIGH)
		self.pwm.ChangeDutyCycle(8+buff)
		time.sleep(5)
		GPIO.output(self.servo_pin,GPIO.LOW)
		time.sleep(0.1)
	
	def down(self,buff=0):
		GPIO.output(self.servo_pin,GPIO.HIGH)
		self.pwm.ChangeDutyCycle(5.5+buff)
		time.sleep(5)
		GPIO.output(self.servo_pin,GPIO.LOW)
		time.sleep(0.1)

	def move(self,ref):
		GPIO.output(self.servo_pin,GPIO.HIGH)
		self.pwm.ChangeDutyCycle(ref)
		time.sleep(0.2)
		GPIO.output(self.servo_pin,GPIO.LOW)
		time.sleep(0.1)
		
	def stop(self):
		self.pwm.stop(0)

	def calibration(self):
		return

class ArmPg():
	def __init__(self,servo_pin):
		self.servo_pin = servo_pin
		
	def setup(self):
		self.pi = pg.pi()
		self.pi.set_mode(self.servo_pin,pg.OUTPUT)

	def up(self,buff=0):
		self.pi.write(self.servo_pin,1)
		self.pi.set_servo_pulsewidth(self.servo_pin,1950)
		time.sleep(1)
		self.pi.set_servo_pulsewidth(self.servo_pin,0)
		self.pi.write(self.servo_pin,0)

	def down(self,buff=0):
		self.pi.write(self.servo_pin,1)
		self.pi.set_servo_pulsewidth(self.servo_pin,1400)
		time.sleep(0.5)
		self.pi.set_servo_pulsewidth(self.servo_pin,0)
		self.pi.write(self.servo_pin,0)

	def move(self,ref):
		self.pi.write(self.servo_pin,1)
		self.pi.set_servo_pulsewidth(self.servo_pin,ref)
		time.sleep(0.5)
		self.pi.set_servo_pulsewidth(self.servo_pin,0)
		self.pi.write(self.servo_pin,0)
		
	def stop(self):
		self.pi.stop()

	def calibration(self):
		return

if __name__ == "__main__":
	arm = ArmPg(23)
	#arm = Arm(23)
	arm.setup()
	arm.up()
	arm.down()
	start = time.time()
	while True:
		end = time.time()
		print("wating")
		if end-start > 5:
			break
	#GPIO.cleanup()
	
		
