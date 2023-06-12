"""
モータの出力まで行う実験用
"""
import numpy as np
import cv2
import sys
import time
import datetime
# import motor
from power_planner import power_planner


# GPIO.setwarnings(False)
# Motor1 = motor.motor(6,5,13)
# Motor2 = motor.motor(20,16,12)
 
closeness = True # 現時点で変更されることはありません

start_time = time.time()
def main():
    cap = cv2.VideoCapture(1)
    while True:
        # camera
        ret,frame = cap.read()
        if ret is False:
            print("cannot read image")
            continue
        commands = power_planner(frame)
        if closeness:
            # Motor1.go(commands["R"])
            # Motor2.go(commands["L"])
            print(commands["R"])
            print(commands["L"])
        else:
            print("`接近完了")
        cv2.imshow('frame',frame)
        # キーボード入力待ち
        key = cv2.waitKey(1) & 0xFF

        # qが押された場合は終了する
        if key == ord('q'):
            break
    cv2.destroyAllWindows()
main()
# GPIO.cleanup()



