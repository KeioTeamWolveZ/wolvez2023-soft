#実際にモーター買って試してみないとわからないかも、コードはこれでいけると思うんだけど...

import RPi.GPIO as GPIO
import sys
import time
import motor

class motor_cmd():
	def __init__(self):
		self.Motor2 = motor.motor(6,5,13)
		self.Motor1 = motor.motor(20,16,12)
	def move(self,Vr=0,Vl=0,t=0.1):
		"""
		arg:
			Vr : right motor output power. -100 ~ 100   (range v<-40,40<v)
			Vl : left motor output power. -100 ~ 100    (range v<-40,40<v)
			 t : time 
		return:
			none : motor output
		"""
		if Vr>=0:
			if Vr>100:
				Vr=0
			self.Motor1.go(Vr)
		else:
			if Vr<-100:
				Vr=0
			self.Motor1.back(-Vr)
			
		if Vl>=0:
			if Vl>100:
				Vl=0
			self.Motor2.go(Vl)
		else:
			if Vl<-100:
				Vl=0
			self.Motor2.back(-Vl)
		
		time.sleep(t)
		
		self.Motor1.stop()
		self.Motor2.stop()
		
mo = motor_cmd()
mo.move(50,-40,1)
