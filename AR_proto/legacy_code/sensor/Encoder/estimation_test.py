import motor
import estimation
import math
import constant as ct
import RPi.GPIO as GPIO
import time
from math import sqrt
import bno055
from math import radians
from math import sin
from math import fabs

GPIO.setwarnings(False)
MotorR = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
MotorL = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
# Encoder = estimation.estimation(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.RIGHT_MOTOR_ENCODER_B_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_B_PIN)
bno055 = bno055.BNO055()

bno055.setupBno()
x=0
y=0
q=0
del_t=0.2
hantei = 0
state = 1
k = 20
v_ref = 70
x_remind = []
y_remind = []
q_remind = []
# MotorR.stop()
# MotorL.stop()

start_time=time.time()
print("cansat-x :",x,"[m]")
print("cansat-y :",y,"[m]")
print("cansat-q :",q,"[rad]")

try:
    print("motor run")
#     MotorR.stop()
#     MotorL.stop()
    x_remind.append(0)
    y_remind.append(0)
    bno055.bnoread()
    q=radians(round(bno055.ex,3))
    time.sleep(2)
    error=math.sin(math.radians(0)) - math.sin(q)
    ke=k*error

    MotorL.go(v_ref+ke)
    MotorR.go(v_ref-ke)
#     MotorR.back(60)
#     MotorL.go(60)
#     bno055.bnoread()
    t_new = time.time()
    while True:
        error=math.sin(math.radians(0)) - math.sin(q)
        ke=k*error

        MotorL.go(v_ref+ke)
        MotorR.go(v_ref-ke)
#         t1=time.time()
        t1 = time.time()
#         cansat_speed,cansat_rad_speed=Encoder.est_v_w(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)
        t2 = time.time()
        print("odometri time:", t2-t1)
        #time.sleep(del_t)
#        t2=time.time()
        bno055.bnoread()
        q=radians(round(bno055.ex,3))
        t_old = t_new
        t_new = time.time()
#         x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t_new-t_old,x,y,q)
        x_remind.append(x)
        y_remind.append(y)
#         if sqrt((abs(x_remind[-1]-x_remind[0]))**2 + (abs(y_remind[-1]-y_remind[0]))**2) >= 5:
#             MotorR.stop()
#             MotorL.stop()
#             break
#         print("cansat speed :",cansat_speed,"[m/s]")
#         print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
        print("cansat-x :",x,"[m]")
        print("cansat-y :",y,"[m]")
        print("cansat-q :",math.degrees(q),"[deg]")
        
# bno055.bnoread()
# try:
#     print("motor run")
#     while True:
#         if state == 1:
#             q_remind=[]
#             MotorR.go(86.5)
#             MotorL.go(85)
#             t1=time.time()
# #             print(0)
#             cansat_speed,cansat_rad_speed=Encoder.est_v_w(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)
#             t2=time.time()
#             x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
#             bno055.bnoread()
#             q=radians(round(bno055.ex,3))
#             print("cansat speed :",cansat_speed,"[m/s]")
#             print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
#             print("cansat-x :",x,"[m]")
#             print("cansat-y :",y,"[m]")
#             print("cansat-q :",q,"[rad]")
#             print("cansat-q :",bno055.ex,"[degree]")
#             print("sin",sin(q))
#             x_remind.append(x)
#             y_remind.append(y)
#             if sqrt((abs(x_remind[-1]-x_remind[0]))**2 + (abs(y_remind[-1]-y_remind[0]))**2) >= 10:
#                 state = 2
#         elif state == 2:
#             x_remind=[]
#             y_remind = []
# #             print("motor curve") 
#             MotorR.go(90)
#             MotorL.go(30)
#             t1=time.time()
#             cansat_speed,cansat_rad_speed=Encoder.est_v_w_for_c(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)
#             t2=time.time()
#             x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t2-t1,x,y,q)
#             bno055.bnoread()
#             q=round(bno055.ex,6)
#             print("cansat speed :",cansat_speed,"[m/s]")
#             print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
#             print("cansat-x :",x,"[m]")
#             print("cansat-y :",y,"[m]")
#             print("cansat-q :",q,"")
#             print("sin",sin(radians(q)))
#             q_remind.append(radians(q))
#             """
#             if sin((abs(q_remind[-1]-q_remind[0])))>=0.9:
#                 state = 1
#                 """
#             if fabs(q-90)<3:
#                 state=1
#         elif state == 3:
#             MotorR.go(81)
#             MotorL.go(80)
            

# try:
#     print("motor run") 
#     MotorR.back(80)
#     MotorL.go(80)
#     
#     while hantei == 0:
#         hantei = Encoder.callback2(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)
#         if hantei == 1:
#             break
#     MotorR.stop()
#     MotorL.stop()
#     GPIO.cleanup()
        
    #time.sleep(1)
except KeyboardInterrupt:
    
    MotorR.stop()
    MotorL.stop()
    bno055.bnoread()
    q=round(bno055.ex,6)
    q=radians(round(bno055.ex,3))
    t_old = t_new
    t_new = time.time()
#     x,y,q=Encoder.odometri(cansat_speed,cansat_rad_speed,t_new-t_old,x,y,q)
#     print("cansat speed :",cansat_speed,"[m/s]")
#     print("cansat rad speed :",cansat_rad_speed,"[rad/s]")
    print("cansat-x :",x,"[m]")
    print("cansat-y :",y,"[m]")
    print("cansat-q :",q,"[rad]")
    end_time=time.time()
    print("motor stop")
    print(end_time-start_time,"[s]")
    
    GPIO.cleanup()

GPIO.cleanup()
