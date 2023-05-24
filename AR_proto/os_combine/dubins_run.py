import motor
import time
import constant as ct
import numpy as np
import matplotlib.pyplot as plt

from DubinsPlan import *

# GPIO.setwarnings(False)
Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

class Dubins_runner():
    global Motor1, Motor2
    is_planning = False
    is_navigation = False
    is_running = False
    dubins_state = 0
    
    def __init__(self):
        self.thre_const = [ct.R_THRE,ct.L_THRE,ct.S_THRE]
        self.start: int
        self.end: int
    
    def planner(self,info):
        self.info = info
        xs,ys,yaws,plan = self.detect_target(info)
        thresholds = self.get_thres(self.dubins_state)
        self.is_planning = False
        self.is_navigation = True
        return xs,ys,yaws,plan
    
    def navigator(self,plan):
        if not self.is_running:
            mr,ml = self.get_motor_vref(plan[self.dubins_state][0])
            self.__runner(mr,ml)
            self.start = time.time()
            self.is_running = True
        else:
            self.end = time.time()
            if self.end-self.start >= self.thresholds:
                self.__stopper()
                self.is_running = False
                self.dubins_state += 1
                if self.dubins_state <= 2:
                    self.get_thres(self.dubins_state)
                else:
                    self.is_navigation = False
    
    def __runner(self,mr,ml):
        Motor1.go(mr)
        Motor2.go(ml)
    
    def __stopper(self):
        Motor1.stop()
        Motor2.stop()

    def get_thres(self, dubins_state):
        self.thresholds = self.thre_const[dubins_state]*self.plan[dubins_state][1]
    
    def get_motor_vref(self,phase):
        if phase == "L":  # left turn
            #print("Turning Left")
            mr = 0
            ml = 70
        elif phase == "S":  # Straight
            #print("Srtaight down")
            mr = 70
            ml = 70
        elif phase == "R":  # right turn
            #print("Srtaight down")
            mr = 70
            ml = 70
        return mr,ml
    
    def detect_target(self,info):
        l_arm = 0.1
        x1 = info["1"]["x"]
        y1 = info["1"]["z"]
        x2 = info["2"]["x"]
        y2 = info["2"]["z"]

        xc = (x1+x2)/2
        yc = (y1+y2)/2
        norm = np.sqrt((x1-x2)**2+(y1-y2)**2)
        xs = xc-l_arm*(y1-y2)/norm
        ys = yc+l_arm*(x1-x2)/norm

        yaws = np.rad2deg(np.arccos((y1-y2)/norm))
        dubins = DubinsPath()
        plan=dubins.dubinspath(0.0,0.0,0.0,xs,ys,yaws,0.03)
        # self.plot_dubinspath(x1,y1,x2,y2,xs,ys)

        return xs,ys,yaws,plan

    def plot_dubinspath(self,x1,y1,x2,y2,xs,ys):
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111)
        ax.plot(x1,y1,'.')
        ax.plot(x2,y2,'.')
        ax.plot(xs,ys,'*')
        ax.plot(0,0,'s')
        ax.set_xlim(-0.3,0.3)
        ax.set_ylim(-0.3,0.3)
        ax.set_aspect('equal', adjustable='box')
        plt.show()