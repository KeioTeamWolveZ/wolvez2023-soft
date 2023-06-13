#実際にモーター買って試してみないとわからないかも、コードはこれでいけると思うんだけど...

import RPi.GPIO as GPIO
import sys
import time

class motor():
    def __init__(self,pin1,pin2,vref): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(pin1, GPIO.OUT)
        GPIO.setup(pin2, GPIO.OUT)
        GPIO.setup(vref, GPIO.OUT)
        self.pin1 = pin1 #入力1
        self.pin2 = pin2 #入力2
        self.vref = vref #電圧を参照するピン PWM
        self.velocity = 0
        self.pwm = GPIO.PWM(vref,490) #電圧を参照するピンを周波数50HZに指定（Arduinoはデフォルトで490だけど、ラズパイはネットだと50HZがメジャーそうだった）
        GPIO.output(self.pin1,GPIO.LOW)
        GPIO.output(self.pin2,GPIO.LOW)
        
#正転
    def go(self,v):
        if v>100:
            v=0
        if v<0:
            v=0 #vに辺な値があった時の処理のための4行,backのも同じ
        self.velocity=v #vは0から100のDuty比、速度を表す指標として利用、後々stopslowlyで使用
        GPIO.output(self.pin1,GPIO.HIGH)
        GPIO.output(self.pin2,GPIO.LOW)
        self.pwm.start(v)#Duty比の指定、以下同様
        
#逆転        
    def back(self,v):
        if v>100:
            v=0
        if v<0:
            v=0
        self.velocity=-v
        GPIO.output(self.pin1,GPIO.LOW)
        GPIO.output(self.pin2,GPIO.HIGH)
        self.pwm.start(v)
        # print(v)
        
#回転ストップ
    def stop(self):
        self.velocity=0
        self.pwm.stop(0)
        GPIO.output(self.pin1,0)
        GPIO.output(self.pin2,0)
        
#徐々に回転遅くして最終的にストップ
    def stopslowly(self):
        if not self.velocity==0:
            for _velocity in range(self.velocity,0,-10): #少しずつDuty比を落として速度を落とす、-10のところは実験によって変えられそう
                self.pwm.ChangeDutyCycle(_velocity)
                GPIO.output(self.pin1,1)
                GPIO.output(self.pin2,0)
                time.sleep(0.5)
            self.velocity=0
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.pin1,0)
        GPIO.output(self.pin2,0)
        
#ブレーキ（何であるんだろう？）
    def brake(self):
        self.velocity=0
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.pin1,1)
        GPIO.output(self.pin2,1)