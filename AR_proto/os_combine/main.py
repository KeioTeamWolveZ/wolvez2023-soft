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
from black_extractor import get_color_hsv

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

#色認識のbool値
aprc_c = True

#sousitu count
c=0

# Main loop
try:
    loop_start = time.time()
    loop_count = 0
    while True:
        loop_count += 1
        # capture and detect markers
        img = pc2.capture(1)
        #rgb_info = cd.get_color_rgb(img)
        #hsv_info = cd.get_color_hsv(img)
        #print(f"\n\nRGB info : {rgb_info}\nHSV info : {hsv_info}")
        # extract brack
        black_img = get_color_hsv(img)
        # Adding space for detected information
        # img = tg.addSpace(img)
        detected_img, ar_info = tg.detect_marker(img)
        #img = tg.addSpace(img)
        pc2.show(img)
        
        if "1" in ar_info.keys() and "2" in ar_info.keys():
            c = 0 #喪失カウントをリセット
            x = ar_info['1']['x'] 
            norm = ar_info['1']['norm']
            arg = tg.theta(ar_info)
            AR_powerplan = AR_powerplanner(ar_info)
            aprc_c = AR_powerplan["C"] #アプローチの仕方のbool
            Motor2.go(AR_powerplan["R"])
            Motor1.go(AR_powerplan["L"])
            time.sleep(0.1)
            print("R:",AR_powerplan["R"],"L:",AR_powerplan["L"]) 
            Motor2.stop()
            Motor1.stop()
        
        else:
            if aprc_c : #色認識による出力決定するかどうか
                
                plan_color = power_planner(img)
                if plan_color["Detected_tf"]:
                    c = 0 #喪失カウントをリセット
                    Motor2.go(plan_color["R"])
                    Motor1.go(plan_color["L"])
                    # print("detected color")
                    print("R:",plan_color["R"],"L:",plan_color["L"]) 
                else :
                    if c > 10:
                        Motor2.go(40) #旋回用
                        time.sleep(0.3)
                        Motor2.stop()
                        # Motor1.stop()
                    c += 1
            else:
                if c > 10:
                    aprc_c = True #色認識をさせる
                c += 1



            
        if save_video : pc2.write_video(detected_img)

        # time.sleep(0.1)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    if save_video : pc2.video.release()
    pc2.stop()
    GPIO.cleanup()
except KeyboardInterrupt:
    loop_end = time.time()
    print(loop_count/(loop_end-loop_start))
    time.sleep(5)
    if save_video : pc2.video.release()
    pc2.stop()
    GPIO.cleanup()
