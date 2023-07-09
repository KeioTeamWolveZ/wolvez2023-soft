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
# from dubinspath_from_AR import detect_target
from power_planner import power_planner
from AR_powerplanner import AR_powerplanner
from black_extractor import get_color_hsv
# arm controller
from connecting_check import arm_grasping, checking # class hi-taiou

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
Flag_AR = False
Flag_C = False
aprc_clear = False
connecting_state = 1

# AR Marker
arm_id = "3"

#sousitu count
c=0


# Main loop
try:
    loop_start = time.time()
    loop_count = 0
    APRC_STATE = False
    while True:
        print('connecting_state:',connecting_state)
        loop_count += 1
        # capture and detect markers
        pc2.picam2.set_controls({"AfMode":0,"LensPosition":4.8})
        img = pc2.capture(1)
        
        #rgb_info = cd.get_color_rgb(img)
        #hsv_info = cd.get_color_hsv(img)
        #print(f"\n\nRGB info : {rgb_info}\nHSV info : {hsv_info}")
        # extract brack
        black_img = get_color_hsv(img)
        # Adding space for detected information
        # img = tg.addSpace(img)
        #pc2.picam2.set_controls({"AfMode":0,"LensPosition":6.5})
        img2 = pc2.capture(1)
        detected_img, ar_info = tg.detect_marker(img)
        print(ar_info)
        #img = tg.addSpace(img)
        
        pc2.show(img)
        #pc2.show(img2,'realtime2')
        if connecting_state == 0:
                target_id = "2"
                arm_id = "3"
        else:
                target_id = "4"
                arm_id= "4"
                
        if target_id in ar_info.keys() and arm_id in ar_info.keys():
            # print('ar_aprc!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            c = 0 #喪失カウントをリセット
            aprc_c = False #アプローチの仕方のbool
            #x = ar_info[arm_id]['x'] #使ってなさそう
            tg.estimate_norm = ar_info[target_id]['norm'] #使u
            #print(tg.estimate_norm)
            # arg = tg.theta(ar_info) #使ってなさそう
            if not Flag_AR:
                print("keisoku_AR")
                starttime_AR = time.time()
                Flag_AR = True
            if Flag_AR and time.time()-starttime_AR >= 1.0:
                Flag_AR = False #フラグをリセット
                AR_powerplan = AR_powerplanner(ar_info,connecting_state)
                APRC_STATE = AR_powerplan['aprc_state']
                if not APRC_STATE:
                        if AR_powerplan["R"] > -0.1:
                                Motor2.go(AR_powerplan["R"])
                                Motor1.go(AR_powerplan["L"])
                                time.sleep(0.1)
                                Motor2.stop()
                                Motor1.stop()
                                print("-AR- R:",AR_powerplan["R"],"L:",AR_powerplan["L"]) 
                        else:
                                
                                Motor2.back(-AR_powerplan["R"])
                                Motor1.back(-AR_powerplan["L"])
                                time.sleep(0.3)
                                Motor2.stop()
                                Motor1.stop()
                                print("Back!")
                                #arm_grasping()
                else:
                        Motor2.stop()
                        Motor1.stop()
                        print('state_change')
                        #arm_grasping()
                        #checking(img,connecting_state)
                        connecting_state += 1
        else:
            
            if aprc_c : #色認識による出力決定するかどうか
                
                plan_color = power_planner(img,connecting_state)
                aprc_clear = plan_color["Clear"]
                if plan_color["Detected_tf"] :
                    #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    if not Flag_C:
                        starttime_color = time.time()
                        Flag_C = True
                        print("keisoku_color")
                        '''
                        Flag(bool値)を使って待機時間の計測を行うための時間計測開始部分
                        '''
                    
                    if Flag_C and time.time()-starttime_color >= 2.0:
                        '''
                        5秒超えたら入ってくる
                        '''
                        c = 0 #喪失カウントをリセット
                        Flag_C = False #フラグをリセット
                        sleep_time = plan_color["w_rate"] * 0.05 + 0.1 ### sleep zikan wo keisan
                        if not aprc_clear: ### go janakute back wo yobu hituyou ga aru
                                Motor2.go(plan_color["R"])
                                Motor1.go(plan_color["L"])
                                # print("detected color")
                                time.sleep(0.2)
                                print("-Color- R:",plan_color["R"],"L:",plan_color["L"])
                                '''
                                色認識の出力の離散化：出力する時間を0.2秒に
                                '''
                        else:
                                if plan_color["R"] > -0.1:
                                        Motor2.back(plan_color["R"])
                                        Motor1.go(plan_color["L"])
                                        time.sleep(sleep_time)
                                        print("R_rotate:",plan_color["R"],"sleep_time:",sleep_time)
                                else:
                                        Motor2.go(-plan_color["R"])
                                        Motor1.back(-plan_color["L"])
                                        time.sleep(sleep_time)
                                        print("L_rotate:",-plan_color["R"],"sleep_time:",sleep_time) 
                    
                        Motor2.stop()
                        Motor1.stop()
                        '''
                        動いた後にストップさせる
                        '''
                else :
                    if c > 10 and not aprc_clear:
                        '''
                        数を10に変更
                        '''
                        Flag_C = False #色を見つけたら待機できるようにリセット
                        Flag_AR = False #AR認識もリセット
                        aprc_clear = False #aprc_clearのリセット
                        Motor2.go(40) #旋回用
                        print("-R:40-")
                        if tg.estimate_norm > 0.5:
                                time.sleep(0.2)
                                print('sleeptime : 0.2')
                        else:
                                time.sleep(0.1)
                                print('sleeptime : 0.1')
                        Motor2.stop()
                        # Motor1.stop()
                        c = 0
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
