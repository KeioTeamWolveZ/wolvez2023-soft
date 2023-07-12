import RPi.GPIO as GPIO
#import wiringpi as wp
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
		self.pwm.ChangeDutyCycle(8+buff)
		time.sleep(0.5)
	
	def down(self,buff=0):
		self.pwm.ChangeDutyCycle(5.5+buff)
		time.sleep(0.5)

	def move(self,ref):
		self.pwm.ChangeDutyCycle(ref)
		time.sleep(0.2)
		
	def stop(self):
		self.pwm.stop(0)

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
	arm.down()
	start = time.time()
	while True:
		end = time.time()
		print("wating")
		if end-start > 5:
			break
	GPIO.cleanup()
	
		
