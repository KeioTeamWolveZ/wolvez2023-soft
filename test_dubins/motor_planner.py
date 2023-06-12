from DubinsPlan import *
#from test_motor_for_dubins import *
#import RPi.GPIO as GPIO

dubins = DubinsPath()

#GPIO.setwarnings(False)
#MotorR = motor.motor(6,5,13)
#MotorL = motor.motor(20,16,12)

def Dubins_to_Motor(start,end,radius):
    
    plan = dubins.dubinspath(start[0],start[1],start[2],end[0],end[1],end[2],radius)
    #print(plan[0])
    for i in [0,1,2]:
        if plan[i][0] == "L":  # left turn
            print("motor left:",plan[i][1])
            #MotorL.go(??)
            #MotorL.stop()
        elif plan[i][0] == "S":  # Straight
            print("motor straight:",plan[i][1])
            #MotorL.go(??)
            #MotorR.go(??)
            #MotorL.stop()
            #MotorR.stop()
        elif plan[i][0] == "R":  # right turn
            print("motor right:",plan[i][1])
            #MotorR.go(??)
            #MotorR.stop()

start=[0.0,0.0,0.0]
end=[7.0,10.0,90.0]
radius = 3.0

Dubins_to_Motor(start,end,radius)













