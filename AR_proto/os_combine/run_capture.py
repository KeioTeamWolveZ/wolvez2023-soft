import numpy as np
import cv2
from cv2 import aruco
import sys
import time
import datetime

# import made package
#from mission_pkg import *
import libcam_module

# import modules
import ar_module
#from ar_module import Target, find_vec
# from dubins_module import Dubins_runner
# import libcam
#from color_det import ColorDetection
import motor
import RPi.GPIO as GPIO
from dubinspath_from_AR import detect_target

save_video = True

# instantiate objects from classes
tg = ar_module.Target()
pc2 = libcam_module.Picam()
#cd = ColorDetection()

# GPIO.setwarnings(False)
Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

# setting wheather to save a video
if save_video : pc2.setup_video("test")

start_time = time.time()
# Main loop

Motor2.go(25)
Motor1.go(25)


while time.time() - start_time < 5:
#while True:
    print(time.time() - start_time)
    img = pc2.capture(1)
    img = tg.addSpace(img)
    detected_img, ar_info = tg.detect_marker(img)
    
    
    pc2.show(detected_img)
        
    if save_video : pc2.write_video(detected_img)

    # time.sleep(0.1)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
        
Motor2.stop()
Motor1.stop()

if save_video : pc2.video.release()
pc2.stop()
GPIO.cleanup()

