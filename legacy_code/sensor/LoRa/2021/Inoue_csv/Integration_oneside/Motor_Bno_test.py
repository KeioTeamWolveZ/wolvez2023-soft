#ライブラリの読み込み
import time
import RPi.GPIO as GPIO
import sys
import numpy as np
import datetime
import os
import constant as ct
import math
import motor
import bno055

GPIO.setmode(GPIO.BCM) #GPIOの設定

#オブジェクトの生成
rightmotor = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
leftmotor = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
bno055 = bno055.BNO055()

bno055.setupBno()

def integ():
    rightmotor.go(60)
    leftmotor.go(60)

def keyboardinterrupt():
    rightmotor.stop()
    leftmotor.stop()

def motor_straight():
    k=20
    vref=90
    error=0
    bno055.bnoread()
    print(bno055.ex)
    if case==1:        
        error=math.sin(math.radians(0)) - math.sin(math.radians(bno055.ex))
        ke=k*error

        leftmotor.go(vref+ke)
        rightmotor.go(vref)
#         vl=vref+ke
#         vr=vref
#         print("vl:" + str(vl) + ", vr:" + str(vr))
#     return ke
    elif case==2:
        error=math.cos(math.radians(270)) - math.cos(math.radians(bno055.ex))
        ke=k*error
        leftmotor.go(vref+ke)
        rightmotor.go(vref)
        vl=vref+ke
        vr=vref
        print("vl:" + str(vl) + ", vr:" + str(vr))
    
    elif case==3:
        error=math.sin(math.radians(180)) - math.sin(math.radians(bno055.ex))
        ke=k*error
        leftmotor.go(vref)
        rightmotor.go(vref+ke)
        vl=vref
        vr=vref+ke
        print("vl:" + str(vl) + ", vr:" + str(vr))

    elif case==0:
        error=math.cos(math.radians(90)) - math.cos(math.radians(bno055.ex))
        ke=k*error
        leftmotor.go(vref)
        rightmotor.go(vref+ke)
        
        vl=vref
        vr=vref+ke
        print("vl:" + str(vl) + ", vr:" + str(vr))

try:
    while True:
        
        case=1
        motor_straight()
        
#         e=motor_straight()
#         print('left:',str(90+e),'   ,right:90')

        time.sleep(0.05)
     
except KeyboardInterrupt:
    print('finished')
    rightmotor.stop()
    leftmotor.stop()
    GPIO.cleanup()
    pass