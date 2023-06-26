import time
import RPi.GPIO as GPIO
import sys
import numpy as np
import bno055_conf


class bno:
      def __init__(self):
            GPIO.setmode(GPIO.BCM) #GPIOの設定
            self.bno055 = bno055_conf.BNO055()
            self.bno055.setupBno()
            
      def get_data(self):
            if self.bno055.begin() is not True:
                  print("Error initializing device")
                  exit()
            self.bno055.bnoread()
            self.bno055.ax=round(self.bno055.ax,3)
            self.bno055.ay=round(self.bno055.ay,3)
            self.bno055.az=round(self.bno055.az,3)
            self.bno055.gx=round(self.bno055.gx,3)
            self.bno055.gy=round(self.bno055.gy,3)
            self.bno055.gz=round(self.bno055.gz,3)
            self.bno055.ex=round(self.bno055.ex,3)
            self.bno055.ey=round(self.bno055.ey,3)
            self.bno055.ez=round(self.bno055.ez,3)
            accel="ax="+str(self.bno055.ax)+","\
                  +"ay="+str(self.bno055.ay)+","\
                  +"az="+str(self.bno055.az)
            grav="gx="+str(self.bno055.gx)+","\
                  +"gy="+str(self.bno055.gy)+","\
                  +"gz="+str(self.bno055.gz)
            euler="ex="+str(self.bno055.ex)+","\
                  +"ey="+str(self.bno055.ey)+","\
                  +"ez="+str(self.bno055.ez)
            print(euler) 
            
            # time.sleep(0.5)
            return accel, grav, euler
