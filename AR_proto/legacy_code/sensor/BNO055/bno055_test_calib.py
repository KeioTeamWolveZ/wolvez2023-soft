import time
import RPi.GPIO as GPIO
import sys
import numpy as np
import bno055

GPIO.setmode(GPIO.BCM) #GPIOの設定
bno055 = bno055.BNO055()
bno055.setupBno()


# bno055.setupBno()

if bno055.begin() is not True:
    print("Error initializing device")
    exit()
    
try:
    while True:
        bno_sys, bno_gyr, bno_acc, bno_mag = bno055.getCalibration()
        print(bno055.getCalibration())
        print(bno_sys)
        time.sleep(0.1)
        if bno_mag == 3:
            print("### End Calibration")
            print("### Set Zero")
            time.sleep(5)
#             bno055.bnoInitial()
            print("### Finish Setting")
#             time.sleep(5)
            break
        
    while True:
        bno055.bnoread()
        bno055.ax=round(bno055.ax,3)
        bno055.ay=round(bno055.ay,3)
        bno055.az=round(bno055.az,3)
        bno055.gx=round(bno055.gx,3)
        bno055.gy=round(bno055.gy,3)
        bno055.gz=round(bno055.gz,3)
        bno055.ex=round(bno055.ex,3)
        bno055.ey=round(bno055.ey,3)
        bno055.ez=round(bno055.ez,3)
        accel="ax="+str(bno055.ax)+","\
              +"ay="+str(bno055.ay)+","\
              +"az="+str(bno055.az)
        grav="gx="+str(bno055.gx)+","\
              +"gy="+str(bno055.gy)+","\
              +"gz="+str(bno055.gz)
        euler="ex="+str(bno055.ex)+","\
              +"ey="+str(bno055.ey)+","\
              +"ez="+str(bno055.ez)
        print(euler) 
        print(bno055.getCalibration())      
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
    pass
