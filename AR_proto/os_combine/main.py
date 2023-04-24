import numpy as np
import cv2
from cv2 import aruco
import sys
import time
import datetime

# import ar_module
from ar_module import Target, find_vec
import motor
import RPi.GPIO as GPIO

save_video = False


# ar = Ar_cansat()
tg = Target()


# GPIO.setwarnings(False)
# Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)




if save_video : tg.setup_video("goal_check")

while True:
    img = tg.capture(1)
    img = tg.addSpace(img)
    detected_img, ar_info = tg.detect_marker(img)
    tg.show(detected_img)
    
    
   
    if ar_info :
        #print(ar_info)
        
        if "1" in ar_info.keys():
            x=ar_info['1']['x']
            norm=ar_info['1']['norm']
            arg = tg.theta(ar_info)
#             print(norm)
            tg.get_result()
                
            #print(arg)
            #print(x)
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
                #print("-0,01<x<0.01")
#                 pass
#             print(f'{ar_info["1"]["roll"]:.3f} | {ar_info["1"]["pitch"]:.3f} | {ar_info["1"]["yaw"]:.3f}')
            
        else:
            pass
        
            vec_list = tg.find_vec(ar_info)
        #print(vec_list)
        
    if save_video : tg.write_video(detected_img)

    # time.sleep(0.1)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

if save_video : tg.video.release()
tg.picam2.stop()
# tg.cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()

