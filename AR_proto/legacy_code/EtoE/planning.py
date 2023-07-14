# ラズパイで動かす時にはこれコメントアウトをはずこと
import motor
import constant as ct
import RPi.GPIO as GPIO
import bno055
import gps

# from msilib import type_string
import time
import math
from math import sqrt
from math import radians
from math import sin
from math import fabs
from turtle import distance
import numpy as np

# GPIO.setwarnings(False)
# MotorR = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
# MotorL = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
# bno055 = bno055.BNO055()
# bno055.setupBno()
# gps = gps.GPS()
# gps.setupGps()

# ゴール方向の角度から行く方向を決定する関数
def decide_direction(phi):
    if phi >= 20:
        direction_goal = 2
        print("ゴール方向："+str(direction_goal)+" -> 右に曲がりたい")
    elif phi > -20 and phi < 20:
        direction_goal = 1
        print("ゴール方向："+str(direction_goal)+" -> 直進したい")
    else:
        direction_goal = 0
        print("ゴール方向："+str(direction_goal)+" -> 左に曲がりたい")
    return direction_goal

# それぞれの方向に対して実際に行う動作を決める関数
def decide_behavior(direction):
    if direction == 0:
        print("左に曲がる")
    elif direction == 1:
        print("直進する")
    elif direction == 2:
        print("右に曲がる")
    elif direction == 3:
        print("90度回転する")

# それぞれの方向に対して実際に行う動作を決める関数
def decide_behavior_raspi(direction_real, target_azimuth, phi, MotorR, MotorL, bno055):
    bno055.bnoread()
    bno055.ex = round(bno055.ex,3)
    if direction_real == 0:
        print("左に"+str(phi)+"[deg] 曲がる")
        while bno055.ex < target_azimuth - 5 or bno055.ex > target_azimuth + 5:
            MotorR.back(70)
            MotorL.go(70)
            bno055.bnoread()
            bno055.ex = round(bno055.ex,3)
        MotorR.stop()
        MotorL.stop()
    elif direction_real == 1:
        print("直進する")
        bno055.bnoread()
        bno055.ey=round(bno055.ey,3)
        current_y = bno055.ey
        while bno055.ey < current_y + 5 - 0.1 or bno055.ey > current_y + 5 + 0.1:
            MotorR.go(70)
            MotorL.go(70)
            bno055.bnoread()
            bno055.ey=round(bno055.ey,3)
        MotorR.stop()
        MotorL.stop()
    elif direction_real == 2:
        print("右に"+str(phi)+"[deg] 曲がる")
        while bno055.ex < target_azimuth - 5 or bno055.ex > target_azimuth + 5:
            MotorR.go(70)
            MotorL.back(70)
            bno055.bnoread()
            bno055.ex = round(bno055.ex,3)
        MotorR.stop()
        MotorL.stop()
    elif direction_real == 3:
        print("90度回転する")
        current_azimuth = bno055.ex
        while bno055.ex < current_azimuth + 90 - 5 or bno055.ex > current_azimuth + 90 + 5:
            MotorR.back(70)
            MotorL.go(70)
            bno055.bnoread()
            bno055.ex = round(bno055.ex,3)
        MotorR.stop()
        MotorL.stop()

def planning(risk, MotorR, MotorL, bno055, gps):
    goal_position = (35.55518,139.65578)

    count = 0
    start_time = time.time()
    while count < 10:
        count += 1
        # GPSから現在の緯度・経度を取得し，ゴールとの方位角を算出
        gps.gpsread()
        datalog ="Time:" + str(gps.Time) + ","\
                    + "緯度:" + str(gps.Lat) + ","\
                    + "経度:" + str(gps.Lon)
        print(datalog)
        gps_dictionary = gps.vincenty_inverse(gps.Lat,gps.Lat,goal_position[0],goal_position[1])
        # print(gps_dictionary)
        theta_goal = gps_dictionary["azimuth1"]

        # 加速度センサからCansatがどの方位角を向いているかを計測
        bno055.bnoread()
        bno055.ex=round(bno055.ex,3)
        theta_cansat = bno055.ex
        print("current cansat azimuth[deg]: "+str(theta_cansat))

        # ゴールの方位角とCansatの前方方位角から，Cansatとゴールの相対角度を算出
        phi = theta_goal - theta_cansat
        print("Cansatとゴールの相対角度[deg]: "+str(phi))
        # direction_goal_deg = np.random.randint(-60,60)  #ゴール方向の角度を取得（後でGPSから値が取れるようにする）

        
        # ゴール方向の角度から左・中央・右のどの方向に行くかを算出
        direction_goal = decide_direction(phi)  #角度から左・前・右のどの方向に進むべきかを取得
        direction_real = direction_goal


        # 危険度行列を取得
        # risk : spm2から出力された危険度

        # risk = np.random.randint(0,100,(2,3))
        print("risk:\n"+str(risk)+"\n")
        # 下の分割領域と上の分割領域にそれぞれ分けて考える
        upper_risk = risk[0,:]
        lower_risk = risk[1,:]
        # 危険度の閾値を決定
        threshold_risk = 70

        # 閾値より小さい値が存在するかどうか確認
        # すべて閾値以上の場合，前方はすべて危険と判断し，画角を変更すべく回転する．
        if np.amin(lower_risk) >= threshold_risk:
            print("前方に安全なルートはありません。90度回転して新たな経路を探索します。")
            direction_real = 3
            decide_behavior_raspi(direction_real, theta_goal, phi, MotorR, MotorL, bno055)

        else:
            if lower_risk[direction_goal] <= threshold_risk:   #ゴール方向の危険度が閾値以下の場合
    #             decide_behavior(direction_real)   # その方向に進む
                decide_behavior_raspi(direction_real, theta_goal, phi, MotorR, MotorL, bno055)
            else:
                print("ゴール方向が安全ではありません。別ルートを探索します。")
                if direction_goal == 0:
                    if lower_risk[1] <= lower_risk[2]:
                        direction_real = 1
                    else:
                        direction_real = 2
    #                 decide_behavior(direction_real)
                    decide_behavior_raspi(direction_real, theta_goal, phi, MotorR, MotorL, bno055)
                    # decide_behavior_raspi(direction_real,MotorR,MotorL)
                elif direction_goal == 1:
                    if lower_risk[0] <= lower_risk[2]:
                        direction_real = 0
                    else:
                        direction_real = 2
                    direction_real = 0
    #                 decide_behavior(direction_real)
                    decide_behavior_raspi(direction_real, theta_goal, phi, MotorR, MotorL, bno055)
                    # decide_behavior_raspi(direction_real,MotorR,MotorL)
                elif direction_goal == 2:
                    if lower_risk[0] <= lower_risk[1]:
                        direction_real = 0
                    else:
                        direction_real = 1
                    # decide_behavior(direction_real)
                    decide_behavior_raspi(direction_real, theta_goal, phi, MotorR, MotorL, bno055)
