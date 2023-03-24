import numpy as np
import cv2
from cv2 import aruco
import sys
import time
import datetime

import ar_module
import vec_calc
import motor
import RPi.GPIO as GPIO

save_video = False


def theta(info):
    x=info['1']['x']
    z=info['1']['z']
    
    norm=np.linalg.norm([x,z])
    theta=np.arcsin(x/norm)
    print(theta)
    return theta

ar = ar_module.Ar_cansat()


# GPIO.setwarnings(False)
# Motor1 = motor.motor(6,5,13)
# Motor2 = motor.motor(20,16,12)




if save_video : ar.setup_video("easy_visual_servo2")

while True:
    img = ar.capture(1)
    img = ar.addSpace(img)
    detected_img, ar_info = ar.detect_marker(img)
    ar.show(detected_img)
    
   
    if ar_info :
        #print(ar_info)
        
#         try:
#             x=ar_info['1']['x']
#             arg=theta(ar_info)
#             print(arg)
#             #print(x)
#             if arg>np.pi/20:
#                 Motor2.go(70)
#                 time.sleep(0.02)
#                 Motor2.stop()
#                 time.sleep(0.5)
#             elif arg<-np.pi/20:
#                 Motor2.back(70)
#                 time.sleep(0.02)
#                 Motor2.stop()
#                 time.sleep(0.5)
#             else:
#                 print("-0,01<x<0.01")
#                 
#         except:
#             pass
        print(ar_info)
        print(vec_calc.find_vec(ar_info))
    if save_video : ar.write_video(detected_img)

    # time.sleep(0.1)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

if save_video : ar.video.release()
ar.cap.release()
cv2.destroyAllWindows()
#GPIO.cleanup()

