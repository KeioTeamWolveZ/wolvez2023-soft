#import RPi.GPIO as GPIO
#import wiringpi as wp
import pigpio as pg
import sys
import time

# 500 ~ 2500

class Arm():
	def __init__(self,servo_pin):
		self.servo_pin = servo_pin
		
	def setup(self):
		self.pi = pg.pi()
		self.pi.set_mode(self.servo_pin,pg.OUTPUT)
		
	def up(self,buff=0):
		self.pi.write(self.servo_pin,1)
		self.pi.set_servo_pulsewidth(self.servo_pin,1500)
		time.sleep(0.5)
		self.pi.set_servo_pulsewidth(self.servo_pin,0)
		self.pi.write(self.servo_pin,0)
	
	def middle(self,buff=0):
		self.pi.write(self.servo_pin,1)
		self.pi.set_servo_pulsewidth(self.servo_pin,1300)
		time.sleep(0.5)
		self.pi.set_servo_pulsewidth(self.servo_pin,0)
		self.pi.write(self.servo_pin,0)
		
	def down(self,buff=0):
		self.pi.write(self.servo_pin,1)
		self.pi.set_servo_pulsewidth(self.servo_pin,1150)
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

# class ArmHardPwm():
# 	def __init__(self,servo_pin):
# 		self.servo_pin = servo_pin
# 		
# 	def setup(self):
# 		wp.wiringPiSetupGpio()
# 		wp.pinMode(self.servo_pin,wp.GPIO.PWM_OUTPUT)
# 		wp.pwmSetMode(wp.GPIO.PWM_MODE_MS)
# 		wp.pwmSetRange(1024)
# 		wp.pwmSetClock(375)

# 	def up(self,buff=0):
# 		wp.pwmWrite(self.servo_pin,110)
# 		time.sleep(0.5)
	
# 	def down(self,buff=0):
# 		wp.pwmWrite(self.servo_pin,74)
# 		time.sleep(0.5)
# 		pass

# 	def move(self,ref):
# 		pass
		
# 	def stop(self):
# 		pass

# 	def calibration(self):
# 		return

if __name__ == "__main__":
	#arm = ArmHardPwm(16)
	arm = Arm(23)
	arm.setup()
	arm.up()
	#arm.move(1800)
	arm.down()
	start = time.time()
	while True:
		end = time.time()
		print("wating")
		if end-start > 1:
			break
	#GPIO.cleanup()
	
		
