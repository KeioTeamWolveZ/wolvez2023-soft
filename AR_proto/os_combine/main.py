import numpy as np
import cv2
from cv2 import aruco
import sys
import time
import datetime

# import made package
#from mission_pkg import *

# import modules
# from ar_module import Target, find_vec
import ar_module
#from dubins_module import Dubins_runner
import libcam_module
#from color_det import ColorDetection
import motor
import RPi.GPIO as GPIO
from dubinspath_from_AR import detect_target
from power_planner import power_planner
from AR_powerplanner import AR_powerplanner

save_video = True

# instantiate objects from classes
tg = ar_module.Target()
pc2 = libcam_module.Picam()
#dub = dubins_module.DubinsRunner()
#cd = ColorDetection()

# GPIO.setwarnings(False)
Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

# setting wheather to save a video
if save_video : pc2.setup_video("test")


# Main loop
while True:
    # capture and detect markers
    img = pc2.capture(1)
    #rgb_info = cd.get_color_rgb(img)
    #hsv_info = cd.get_color_hsv(img)
    #print(f"\n\nRGB info : {rgb_info}\nHSV info : {hsv_info}")

    # 画閣内の色重心の位置から出力コマンドを決定する　plan_color = {"R":power_R,"L":power_L,"C":bool} で返す
    plan_color = power_planner(img)
    print(plan_color["C"]) 
    Motor2.go(plan_color["R"])
    Motor1.go(plan_color["L"])
    # Adding space for detected information
    img = tg.addSpace(img)
    detected_img, ar_info = tg.detect_marker(img)
    
    pc2.show(detected_img)
    
    if ar_info :
        #print(ar_info)
        
        if "1" in ar_info.keys() and "2" not in ar_info.keys():
            x=ar_info['1']['x']
            norm=ar_info['1']['norm']
            arg = tg.theta(ar_info)
#             print(norm)
            tg.get_result()

            AR_powerplan = AR_powerplanner(ar_info)

            Motor2.go(AR_powerplan["R"])
            Motor1.go(AR_powerplan["L"])
            
            time.sleep(0.3)

            Motor2.stop()
            Motor1.stop()

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
        
        # if "1" in ar_info.keys() and "2" in ar_info.keys():
        #     # DubinsRunner
        #     # if dub.is_planning:
        #     #     xs,ys,yaws,plan = dub.planner(ar_info)
        #     # elif dub.is_navigation:
        #     #     dub.navigator(plan)

            
            
        #     xs,ys,yaws,plan = detect_target(ar_info)
        #     #print(ar_info)
        #     #print(f"xs:{xs} | ys:{ys}| {yaws}")
        #     print(plan)
        #     for i in [0,1,2]:
        #         if plan[i][0] == "L":  # left turn
        #             #print("motor left:",plan[i][1])
        #             Motor2.go(70)
        #             time.sleep(0.3)
        #             Motor2.stop()
        #         elif plan[i][0] == "S":  # Straight
        #             #print("motor straight:",plan[i][1])
        #             Motor2.go(70)
        #             Motor1.go(70)
        #             time.sleep(0.3)
        #             Motor2.stop()
        #             Motor1.stop()
        #         elif plan[i][0] == "R":  # right turn
        #             #print("motor right:",plan[i][1])
        #             Motor1.go(70)
        #             time.sleep(0.3)
        #             Motor1.stop()
        
        vec_list = tg.find_vec(ar_info)
        #print(vec_list)
        
        
    if save_video : pc2.write_video(detected_img)

    # time.sleep(0.1)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

if save_video : pc2.video.release()
pc2.stop()
GPIO.cleanup()

