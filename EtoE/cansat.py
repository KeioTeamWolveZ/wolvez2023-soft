#Last Update 2023/08/06
#Author : Masato Inoue

from tempfile import TemporaryDirectory
from xml.dom.pulldom import default_bufsize
# from pandas import IndexSlice
import RPi.GPIO as GPIO
import sys
import cv2
import time
import numpy as np
import os
import re
import math
from datetime import datetime
from glob import glob
from numpy import arccos, arcsin, arctan2, sin, cos, tan, pi, deg2rad, rad2deg
import shutil
# from math import prod

# import functions
import Wolvez2023
import constant as ct

"""
ステート説明

0. preparing()        準備ステート．センサ系の準備．一定時間以上経過したらステート移行．
1. flying()           放出準備ステート．フライトピンが接続されている状態（＝ボイド缶に収納されている）．フライトピンが外れたらステート移行．
2. droping()          降下&着陸判定ステート．加速度センサの値が一定値以下の状態が一定時間続いたら着陸と判定しステート移行．
3. landing()          分離ステート．分離シートの焼ききりによる分離，モータ回転による分離シートからの離脱を行ったらステート移行．
4. first_releasing()  電池モジュール放出ステート．モジュール放出のための焼き切りのあと，二つ目のモジュール放出のために一定時間走行したらステート移行．
5. second_releasing() 電力消費モジュール放出ステート．モジュール放出のための焼き切りのあと，右旋回をおこなってモジュールを横からみられる位置に移動したらステート移行．
6. connecting()       モジュール接続ステート．電池モジュールに接近・把持を行った後，電力消費モジュールに接近・接続を行い，接続を確認してステート移行．
7. running()          ランバックステート．能代大会ミッション部門では使用しない．ARLISSにおいて，ゴール地点を目指して走行する．ゴールを判定したら走行を終了してステート移行．
8. finish()           終了ステート．

"""

class Cansat():
    def __init__(self,state):
        # GPIO設定
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) #GPIOの設定
        GPIO.setup(ct.const.FLIGHTPIN_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP) #フライトピン用。プルアップを有効化
        GPIO.setup(ct.const.SEPARATION_PARA,GPIO.OUT) #焼き切り用のピンの設定
        GPIO.setup(ct.const.SEPARATION_MOD1,GPIO.OUT) #焼き切り用のピンの設定
        GPIO.setup(ct.const.SEPARATION_MOD2,GPIO.OUT) #焼き切り用のピンの設定
        
        # インスタンス生成用
        self.bno055 = Wolvez2023.BNO055()
        self.MotorL = Wolvez2023.Motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
        self.MotorR = Wolvez2023.Motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN, ct.const.LEFT_MOTOR_VREF_PIN)
        self.gps = Wolvez2023.GPS()
        self.lora = Wolvez2023.lora()
        self.arm = Wolvez2023.Arm(ct.const.SERVO_PIN)
        self.tg = Wolvez2023.Target()
        self.pc2 = Wolvez2023.Picam()
        self.cpp = Wolvez2023.ColorPowerPlanner()
        self.app = Wolvez2023.ARPowerPlanner()
        self.RED_LED = Wolvez2023.led(ct.const.RED_LED_PIN)
        self.BLUE_LED = Wolvez2023.led(ct.const.BLUE_LED_PIN)
        self.GREEN_LED = Wolvez2023.led(ct.const.GREEN_LED_PIN)
        
        #ステート設定用
        self.timer = 0
        self.state = state
        self.landstate = 0
        
        #初期時時間設定
        self.startTime_time=time.time()
        self.startTime = str(datetime.now())[:19].replace(" ","_").replace(":","-")
        self.preparingTime = 0
        self.flyingTime = 0
        self.droppingTime = 0
        self.landingTime = 0
        self.arm_calibTime = 0
        self.modu_sepaTime = 0
        self.starttime_color = time.time()
        self.starttime_AR = time.time()
        self.checking_time = 0
        self.connecting_time = 0
        self.runningTime = 0
        self.finishTime = 0
        self.stuckTime = 0

        # 初期カウンター設定
        self.countFlyLoop = 0
        self.countDropLoop = 0
        self.countstuckLoop = 0
        self.cameraCount = 0
        self.pint_count = 0
        self.pint_change_loop_count = 0
        self.arm_calibCount = 0
        self.avoid_paraCount = 0
        self.ar_count = 0
        self.vanish_c = 0
        self.gpscount = 0
        self.mirror_count = 0
        
        # state管理用変数初期化
        self.startgps_lon=[]
        self.startgps_lat=[]
        self.done_approach = False
        self.ar_checker = False
        self.Flag_AR = False
        self.cl_checker = False
        self.aprc_c = True
        self.Flag_C = False
        self.aprc_clear = False
        self.connected = False
        self.running_finish = False
        self.releasingstate = 0
        self.connecting_state = 0
        self.change_size = 0 # new
        self.mirror = False 
        self.distancing_finish = False
        self.releasing_01 = False
        self.releasing_02 = False
        
        # state内変数初期設定
        self.cam_pint = 9
        self.estimate_norm = 100000
        self.ar_info = {}
        self.cl_data = [0,0,0]
        self.move_arplan = 'none'
        self.move_clplan = 'none'
        self.vanish_stuck = 0
        self.goaldis = 0
        self.goalphi = 0
        self.rv, self.lv = 0, 0
        
        self.dict_list = {}
        self.goallat = ct.const.GPS_GOAL_LAT
        self.goallon = ct.const.GPS_GOAL_LON
        self.saveDir = "results"
        self.mkdir()
        self.mkfile()
        self.mvfile()

    def mkdir(self): #フォルダ作成部分
        self.results_dir = f'results/{self.startTime}'
        self.results_img_dir = self.results_dir + '/imgs'
        os.mkdir(self.results_dir)
        os.mkdir(self.results_img_dir)
        return

    def mkfile(self):
        return

    def mvfile(self):
        return
    
    def writeData(self): #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる
        print_datalog = str(self.timer) + ","\
                  + "state:"+str(self.state)+ ","\
                  + "Time:"+str(self.gps.Time) + ","\
                  + "Lat:"+str(self.gps.Lat).rjust(6) + ","\
                  + "Lng:"+str(self.gps.Lon).rjust(6) + ","\
                  + "ax:"+str(round(self.ax,6)).rjust(6) + ","\
                  + "ay:"+str(round(self.ay,6)).rjust(6) + ","\
                  + "az:"+str(round(self.az,6)).rjust(6) + ","\
                  + "gx:"+str(round(self.gx,6)).rjust(6) + ","\
                  + "gy:"+str(round(self.gy,6)).rjust(6) + ","\
                  + "gz:"+str(round(self.gz,6)).rjust(6) + ","\
                  + "q:" + str(self.ex).rjust(6) + ","\
                  + "rV:" + str(round(self.MotorR.velocity,2)).rjust(4) + ","\
                  + "lV:" + str(round(self.MotorL.velocity,2)).rjust(4) + ","\
                  + "Camera:" + str(self.cameraCount)

        print(print_datalog)
     
        datalog = str(self.timer) + ","\
                  + "state:"+str(self.state) + ","\
                  + "Time:"+str(self.gps.Time) + ","\
                  + "Lat:"+str(self.gps.Lat).rjust(6) + ","\
                  + "Lng:"+str(self.gps.Lon).rjust(6) + ","\
                  + "ax:"+str(self.bno055.ax).rjust(6) + ","\
                  + "ay:"+str(self.bno055.ay).rjust(6) + ","\
                  + "az:"+str(self.bno055.az).rjust(6) + ","\
                  + "q:"+str(self.bno055.ex).rjust(6) + ","\
                  + "Camera:" + str(self.cameraCount)

        mission_log = str(self.timer) + ","\
                    + "state:"+str(self.state) 
        if self.state == 3:
            datalog = datalog + ","\
                 + "rV:"+str(round(self.rv,3)).rjust(6) + ","\
                 + "lV:"+str(round(self.lv,3)).rjust(6) + ","\
                 + "Color-Approach:" + str(self.cl_checker) + ","\
                 + "Color-data: x:" + str(self.cl_data[0])+ "y:"+ str(self.cl_data[1]) + "Area:"+ str(self.cl_data[2]) + ","\
                 + "Color-move:" + str(self.move_clplan)
            if self.landstate == 1:
                datalog = datalog + ","\
                     + "gx:"+str(self.bno055.gx).rjust(6) + ","\
                     + "gy:"+str(self.bno055.gy).rjust(6) + ","\
                     + "gz:"+str(self.bno055.gz).rjust(6) + ","\
                     + "mirror-detection:"+str(self.mirror)
            if self.landstate == 2:
                datalog = datalog +','\
                    + "Para_distancing:"+str(self.distancing_finish)
        elif self.state == 6:
           datalog = datalog + ","\
                 + "rV:"+str(round(self.rv,3)).rjust(6) + ","\
                 + "lV:"+str(round(self.lv,3)).rjust(6) + ","\
                 + "ConnectingState:" + str(self.connecting_state) + ","\
                 + "AR-Approach:" + str(self.ar_checker) + ","\
                 + "AR-info:" + str(self.ar_info) + ","\
                 + "AR-move:" + str(self.move_arplan) + ","\
                 + "Color-Approach:" + str(self.cl_checker) + ","\
                 + "Color-data:x" + str(self.cl_data[0])+ "y:"+ str(self.cl_data[1]) + "Area:"+ str(self.cl_data[2]) + ","\
                 + "Color-move:" + str(self.move_clplan) + ","\
                 + "Done-Approach:" + str(self.done_approach) + ","\
                 + "Done-Connect:" + str(self.connected)
        elif self.state == 7 or self.state == 8:
            datalog = datalog + ","\
                 + "rV:"+str(round(self.MotorR.velocity,3)).rjust(6) + ","\
                 + "lV:"+str(round(self.MotorL.velocity,3)).rjust(6) + ","\
                 + "DistanceToGoal:" + str(self.goaldis) + ","\
                 + "ArgumentToGoal:" + str(self.goalphi)+ ","\
                 + "GoalCheck:" + str(self.running_finish)
        
        with open(f'results/{self.startTime}/control_result.txt',"a")  as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(datalog + '\n')

    def writeMissionlog(self):
        mission_log = str(self.timer) + ","\
                + "state:"+str(self.state) 
        if self.state == 3:
            mission_log = mission_log + ","\
                + "Para_distancing:" + str(self.distancing_finish) # パラから距離を取る
        if self.state == 4:
            mission_log = mission_log + ","\
                + "Releasing_01:"  + str(self.releasing_01) # 電池モジュール焼き切り
        if self.state == 5:
            mission_log = mission_log + ","\
                + "Releasing_02:"  + str(self.releasing_02) # 電力消費モジュール焼き切り
        if self.state == 6:
            mission_log = mission_log + ","\
                + "ConnectingState:" + str(self.connecting_state) + ","\
                + "Done-Approach:" + str(self.done_approach) + ","\
                + "Done-Connect:" + str(self.connected)

        with open(f'results/{self.startTime}/mission_log.txt',"a")  as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(mission_log + '\n')

    def sequence(self):
        if self.state == 0:   #センサ系の準備を行う段階。時間経過でステート移行
            self.preparing()
        elif self.state == 1: #放出を検知する段階。フライトピンが抜けたらステート移行
            self.flying()
        elif self.state == 2: #着陸判定する段階。加速度の値が一定値以下になったら着陸したと判定してステート移行
            self.dropping()
        elif self.state == 3: #焼き切り&パラシュートから離脱したらステート移行
            self.landing()
        elif self.state == 4: #電池モジュール焼き切り&一定時間走行したらステート移行
            self.first_releasing()
        elif self.state == 5: #電力消費モジュール焼き切り&旋回したらステート移行
            self.second_releasing()
        elif self.state == 6: #モジュールの接続段階．接近・把持・接近・接続・接続確認を終えたらステート移行
            self.connecting()
        elif self.state == 7: #ARLISS用のランバックステート．ゴール座標を目指して命絶えるまで爆走する．「ゴールに到達できれば」ステート移行
            self.running()
        elif self.state == 8: #終了
            self.finish()
        else:
            self.state = self.laststate #どこにも引っかからない場合何かがおかしいのでlaststateに戻してあげる

    def setup(self):
        self.gps.setupGps()
        self.bno055.setupBno()
        self.bno055.bnoInitial()
        self.lora.sendDevice.setup_lora()
        self.arm.setup()
        if self.bno055.begin() is not True:
            print("Error initializing device")
            exit()
 
    def sensor(self): #セットアップ終了後
        self.timer = int(1000*(time.time() - self.startTime_time)) #経過時間 (ms)
        self.gps.gpsread()
        self.bno055.bnoread()
        self.ax=round(self.bno055.ax,3)
        self.ay=round(self.bno055.ay,3)
        self.az=round(self.bno055.az,3)
        self.gx=round(self.bno055.gx,3)
        self.gy=round(self.bno055.gy,3)
        self.gz=round(self.bno055.gz,3)
        self.ex=round(self.bno055.ex,3)
        self.lat = round(float(self.gps.Lat),5)
        self.lon = round(float(self.gps.Lon),5)
        
        self.writeData() #txtファイルへのログの保存
    
        if not self.state == 1: #preparingのときは電波を発しない
            self.sendLoRa()

    def preparing(self): #時間が立ったら移行
        if self.preparingTime == 0:
            #self.pc2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
            self.img = self.pc2.capture(0,self.results_img_dir+f'/{self.cameraCount}')
            self.preparingTime = time.time()#時刻を取得
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()

        if not self.preparingTime == 0:
            if self.gpscount <= ct.const.PREPARING_GPS_COUNT_THRE:
                self.startgps_lon.append(float(self.gps.Lon))
                self.startgps_lat.append(float(self.gps.Lat))
                self.gpscount+=1
                
            else:
                print("GPS completed!!")
            
            if time.time() - self.preparingTime > ct.const.PREPARING_TIME_THRE:
                self.startlon=np.mean(self.startgps_lon)
                self.startlat=np.mean(self.startgps_lat)
                self.state = 1
                self.laststate = 1
    
    def flying(self): #フライトピンが外れる➡︎ボイド缶から放出されたことを検出するステート
        if self.flyingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.flyingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()

        if GPIO.input(ct.const.FLIGHTPIN_PIN) == GPIO.HIGH: #highかどうか＝フライトピンが外れているかチェック
            self.countFlyLoop+=1
            if self.countFlyLoop > ct.const.FLYING_FLIGHTPIN_COUNT_THRE: #一定時間HIGHだったらステート移行
                self.state = 2
                self.laststate = 2       
        else:
            self.countFlyLoop = 0 #何故かLOWだったときカウントをリセット
    
    def dropping(self): #着陸判定ステート
        if self.droppingTime == 0: #時刻を取得してLEDをステートに合わせて光らせる
            self.droppingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()
      
        #加速度が小さくなったら着地判定
        if (self.bno055.ax**2 + self.bno055.ay**2 + self.bno055.az**2) < ct.const.DROPPING_ACC_THRE**2: #加速度が閾値以下で着地判定
            self.countDropLoop+=1            
            if self.countDropLoop > ct.const.DROPPING_ACC_COUNT_THRE: #着地判定が複数回行われたらステート以降
                self.state = 3
                self.laststate = 3
        else:
            self.countDropLoop = 0 #初期化の必要あり

    def landing(self): #着陸判定ステート。焼き切り&分離シートからの離脱が必要 -> パラシュートが検知された場合にはよける
        if self.landstate == 0:
            if self.landingTime == 0: #時刻を取得してLEDをステートに合わせて光らせる
                self.landingTime = time.time()
                self.RED_LED.led_off()
                self.BLUE_LED.led_off()
                self.GREEN_LED.led_on()
                
            if not self.landingTime == 0:
                #焼き切りによるパラ分離
                if self.landstate == 0:
                    GPIO.output(ct.const.SEPARATION_PARA,1) #電圧をHIGHにして焼き切りを行う
                    if time.time()-self.landingTime > ct.const.SEPARATION_TIME_THRE:
                        GPIO.output(ct.const.SEPARATION_PARA,0) #焼き切りが危ないのでlowにしておく
                        self.landstate = 1
                        self.pre_motorTime = time.time()
                        self.MotorR.go(ct.const.LANDING_MOTOR_VREF)
                        self.MotorL.go(ct.const.LANDING_MOTOR_VREF)
                        self.landing_lat = round(float(self.gps.Lat),5)
                        self.landing_lon = round(float(self.gps.Lon),5)
        
        #パラシュートの色を検知して離脱
        elif self.landstate == 1:
            # 走行中は色認識されなければ直進，されれば回避
            self.cameraCount += 1
            self.img = self.pc2.capture(0,self.results_img_dir+f'/{self.cameraCount}')
            self.plan_color = self.cpp.para_detection(self.img)
            self.cl_checker = self.plan_color["Detected_tf"]
            self.move_clplan = self.plan_color["move"]
            self.cl_data = self.cpp.pos
            # self.found_color = self.cpp.avoid_color(self.img,self.cpp.AREA_RATIO_THRESHOLD,self.cpp.BLUE_LOW_COLOR,self.cpp.BLUE_HIGH_COLOR)
            if not self.plan_color["Detected_tf"]:
                self.MotorR.go(ct.const.LANDING_MOTOR_VREF)
                self.MotorL.go(ct.const.LANDING_MOTOR_VREF +7)
                self.rv = ct.const.LANDING_MOTOR_VREF
                self.lv = ct.const.LANDING_MOTOR_VREF
                #self.stuck_detection()
            else:
                self.MotorR.go(self.plan_color["R"])
                self.MotorL.go(self.plan_color["L"])
                self.rv = self.plan_color["R"]
                self.lv = self.plan_color["L"]
                #self.stuck_detection()

            if time.time()-self.pre_motorTime > ct.const.LANDING_MOTOR_TIME_THRE: #10秒間モータ回して分離シートから十分離れる
                self.MotorR.stop()
                self.MotorL.stop()
                self.rv = 0
                self.lv = 0
                self.mirror_checker()
                if self.mirror_count > ct.const.MIRROR_COUNT_THRE:
                    self.mirror_count = 0
                    self.stuck_detection()
                    self.pre_motorTime = time.time()
                    self.MotorR.go(ct.const.LANDING_MOTOR_VREF)
                    self.MotorL.go(ct.const.LANDING_MOTOR_VREF +7)
                    
                elif self.mirror:
                    pass
                else:
                    self.landstate = 2
            
            
        if self.landstate == 2:
            dlon = self.landing_lon - self.lon
            # distance to the goal
            self.startdis = ct.const.EARTH_RADIUS * arccos(sin(deg2rad(self.lat))*sin(deg2rad(self.landing_lat)) + cos(deg2rad(self.lat))*cos(deg2rad(self.landing_lat))*cos(deg2rad(dlon)))
            print(f"Distance from landing: {round(self.startdis,4)} [km]")

            # angular to the goal (North: 0, South: 180)
            self.goalphi = 90 - rad2deg(arctan2(cos(deg2rad(self.lat))*tan(deg2rad(self.goallat)) - sin(deg2rad(self.lat))*cos(deg2rad(dlon)), sin(deg2rad(dlon))))
            if self.goalphi < 0:
                self.goalphi += 360
            print(self.goalphi)
            
            self.arg_diff = self.goalphi - (self.ex-0)
            if self.arg_diff < 0:
                self.arg_diff += 360
            
            print(f"Argument to goal: {round(self.arg_diff,2)} [deg]")
            
            if self.runningTime == 0:
                self.runningTime = time.time()
                
            # elif time.time() - self.runningTime < 10:
                # print("inoue_run")
                
            elif self.startdis > ct.const.GOAL_DISTANCE_THRE*5:
                self.MotorR.stop()
                self.MotorL.stop()
                self.goaltime = time.time()-self.runningTime
                self.distancing_finish = True
                self.writeMissionlog() # write mission log
                self.landstate = 3
            
            else:
                
                if self.arg_diff <= 180 and self.arg_diff > 20:
                    self.MotorR.go(ct.const.RUNNING_MOTOR_VREF-15)
                    self.MotorL.go(ct.const.RUNNING_MOTOR_VREF)
                    
                elif self.arg_diff > 180 and self.arg_diff < 340:
                    self.MotorR.go(ct.const.RUNNING_MOTOR_VREF)
                    self.MotorL.go(ct.const.RUNNING_MOTOR_VREF-15)
                
                else:
                    self.MotorR.go(ct.const.RUNNING_MOTOR_VREF)
                    self.MotorL.go(ct.const.RUNNING_MOTOR_VREF)
                
                self.stuck_detection()
                    
                    
            
        elif self.landstate == 3: #アームのキャリブレーション
            print("calib arm")
            if self.arm_calibTime == 0:
                self.arm.up()
                self.arm.down()
                self.arm.middle()
                self.arm_calibTime = time.time()

            if time.time() - self.arm_calibTime < ct.const.ARM_CARIBRATION_THRE:
                self.cameraCount += 1
                self.img = self.pc2.capture(0,self.results_img_dir+f'/{self.cameraCount}')
                detected_img, self.ar_info = self.tg.detect_marker(self.img)
                self.arm.calibration()  # 関数内でキャリブレーションを行う
            else:
                print("\n\n=====The arm was calibrated=====\n\n")
                self.connecting_time = time.time()
                self.state = 4
                self.laststate = 4

            #if "1" in self.ar_info.keys():
            #    if self.ar_info["1"]["y"] - ct.const.ARM_CALIB_POSITION > 0.5:
            #        self.buff = 0.2
            #   elif self.ar_info["1"]["y"] - ct.const.ARM_CALIB_POSITION < 0.5:
            #        self.buff = -0.2
            #   else:
            #       self.arm_calibCount += 1
    def mirror_checker(self):
        if self.gz < 5:
            self.mirror_count += 1
            self.mirror = True 
        else:
            self.mirror_count = 0
            self.mirror = False 
        
        
    def first_releasing(self):
        if self.modu_sepaTime == 0: #時刻を取得してLEDをステートに合わせて光らせる
            self.modu_sepaTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
            
        if not self.modu_sepaTime == 0:
            #焼き切りによるパラ分離
            if self.releasingstate == 0:
                GPIO.output(ct.const.SEPARATION_MOD1,1) #電圧をHIGHにして焼き切りを行う
                if time.time()-self.modu_sepaTime > ct.const.SEPARATION_TIME_THRE:
                    GPIO.output(ct.const.SEPARATION_MOD1,0) #焼き切りが危ないのでlowにしておく
                    self.releasingstate = 1
        
        if self.releasingstate == 1:
            self.MotorR.go(ct.const.RELEASING_MOTOR_VREF)
            self.MotorL.go(ct.const.RUNNING_MOTOR_VREF-20)
            self.pre_motorTime = time.time()
            self.releasingstate = 2
        
        if self.releasingstate == 2:
            if time.time()-self.pre_motorTime > ct.const.RELEASING_MOTOR_TIME_THRE: #5秒間モータ回して一つめのモジュールから十分離れる
                    self.MotorR.stop()
                    self.MotorL.stop()
                    self.modu_sepaTime = 0
                    self.releasingstate = 0
                    self.state = 5
                    self.releasing_01 = True # mission_log
                    self.writeMissionlog() # write mission log
                    self.laststate = 5
    
    def second_releasing(self):
        if self.modu_sepaTime == 0: #時刻を取得してLEDをステートに合わせて光らせる
            self.modu_sepaTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
            
        if not self.modu_sepaTime == 0:
            #焼き切りによるパラ分離
            if self.releasingstate == 0:
                GPIO.output(ct.const.SEPARATION_MOD2,1) #電圧をHIGHにして焼き切りを行う
                if time.time()-self.modu_sepaTime > ct.const.SEPARATION_TIME_THRE-5:
                    GPIO.output(ct.const.SEPARATION_MOD2,0) #焼き切りが危ないのでlowにしておく
                    self.releasingstate = 1
        
        if self.releasingstate == 1:
            self.MotorR.go(ct.const.RELEASING_MOTOR_VREF)
            self.MotorL.go(ct.const.RUNNING_MOTOR_VREF-20)
            self.pre_motorTime = time.time()
            self.releasingstate = 2
        
        elif self.releasingstate == 2:
            if time.time()-self.pre_motorTime > ct.const.RELEASING_MOTOR_TIME_THRE: #5秒間モータ回して分離シートから十分離れる
                    self.pre_motorTime = time.time()
                    self.MotorR.go(ct.const.RELEASING_MOTOR_VREF)
                    self.MotorL.stop()
                    self.releasingstate = 3
                    
        if self.releasingstate == 3:
            if time.time()-self.pre_motorTime > ct.const.TURNING_MOTOR_TIME_THRE: #2 seconds for tuning
                    self.MotorR.stop()
                    self.MotorL.stop()
                    self.modu_sepaTime = 0
                    self.releasingstate = 0
                    self.state = 6
                    self.releasing_02 = True #mission_log
                    self.writeMissionlog() # write mission log
                    self.laststate = 6

    def connecting(self):
        # if time over cansat will give up connecting
        if time.time() - self.connecting_time > ct.const.CONNECTING_TIME_LIMIT:
            self.state = 7
            self.laststate = 7
            print("\nGave up connecting and move on to the running state\n\n")
            self.lora.sendData("GaveUpConnecting")
            with open(f'results/{self.startTime}/control_result.txt',"a")  as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
                test.write('\nGave up connecting and move on to the running state\n\n')
            time.sleep(3)
            
        if self.connecting_state == 2:
            self.arm.middle()
            self.cameraCount += 1
            self.img = self.pc2.capture(0,self.results_img_dir+f'/{self.cameraCount}')
            detected_img, self.ar_info = self.tg.detect_marker(self.img)
            SorF = self.checking(self.img,self.connecting_state-1)
            if SorF["Time_clear"]:
                self.arm.up()
                # self.MotorR.go(-100)
                # self.MotorL.go(100)
                # time.sleep(5.0)
                self.state = 7
                self.laststate = 7
        else:
            self.done_approach = False
            if self.connecting_state == 0:
                self.RED_LED.led_off()
                self.BLUE_LED.led_off()
                self.GREEN_LED.led_on()
                self.arm.up()
            if self.connecting_state == 1:
                self.RED_LED.led_off()
                self.BLUE_LED.led_on()
                self.GREEN_LED.led_off()
                self.arm.up()
            
            # 前傾姿勢になってしまった場合
            if self.gy > 4.5:
                self.arm.down()
                self.arm.up()
                
            # change camera pint loop
            # if self.change_size == 0 and self.pc2.size[1] != 1700:
                # self.pc2.change_size(1400, 1700, self.cam_pint)
            # elif self.change_size == 1 and self.pc2.size[1] != 1300:
                # self.pc2.change_size(1750, 1300, self.cam_pint)
            if self.aprc_clear and not self.ar_checker and self.pint_count > 5 :
                print("here")
                self.pint_change_loop_count = 0
                self.cam_pint = 10.5
                while self.cam_pint > 3.0: # and self.pint_change_loop_count < 3:
                    if not self.ar_checker:
                        self.cam_pint -= 0.5
                        self.pc2.picam2.set_controls({"AfMode":0,"LensPosition":self.cam_pint})
                        
                        # capture and detect markers
                        # self.pc2.picam2.set_controls({"AfMode":0,"LensPosition":9})
                        self.cameraCount += 1
                        self.img = self.pc2.capture(0,self.results_img_dir+f'/{self.cameraCount}')
                        #self.blk = self.pc2.red2blk(self.img)
                        print(self.cam_pint)
                        detected_img, self.ar_info = self.tg.detect_marker(self.img)
                        self.AR_checker = self.tg.AR_decide(self.ar_info,self.connecting_state)
                        self.ar_checker = self.AR_checker["AR"]
                    else:
                        break
                    self.pint_change_loop_count += 1
                if not self.ar_checker: # 探索しても見つからなかったとき
                    self.cam_pint = self.cam_pint
                    self.pc2.picam2.set_controls({"AfMode":0,"LensPosition":self.cam_pint})
                
                # ループを終えたら0に戻す 
                self.pint_count = 0 
                self.pint_change_loop_count = 0

            else:
                # capture and detect markers
                # self.pc2.picam2.set_controls({"AfMode":0,"LensPosition":9})
                self.cameraCount += 1
                self.img = self.pc2.capture(0,self.results_img_dir+f'/{self.cameraCount}')
                #self.blk = self.pc2.red2blk(self.img)
                
                detected_img, self.ar_info = self.tg.detect_marker(self.img)
                self.AR_checker = self.tg.AR_decide(self.ar_info,self.connecting_state)
                self.ar_checker = self.AR_checker["AR"]
            if self.connecting_state == 1 and self.AR_checker["id"] in ["2","11","16"]:
                self.connecting_state = 0 # 青モジュールを落とした場合(id:2と11and16)、connecting_stateを0に戻して再び拾う
                self.move(-60,-60,0.1) # back and retry
            
            print(self.ar_info)
            print(f"id:{self.AR_checker['id']}")
            
            if self.AR_checker["AR"]:
                self.change_size += 1
                self.vanish_c = 0 #喪失カウントをリセット
                self.vanish_stuck = 0 #喪失カウントをリセット
                self.aprc_c = False #アプローチの仕方のbool
                self.estimate_norm = self.AR_checker["norm"] #使u これself.いるん？？
                if not self.Flag_AR:
                    print("keisoku_AR")
                    self.starttime_AR = time.time()
                    self.ar_count += 1
                    self.Flag_AR = True
                if self.Flag_AR and time.time()-self.starttime_AR >= 1.5:
                    self.Flag_AR = False #フラグをリセット←これもAR_decideの中で定義しても良いかも
                    AR_powerplan = self.app.ar_powerplanner(self.ar_info,self.connecting_state,self.AR_checker)  #sideを追加
                    self.move_arplan = AR_powerplan["move"]
                    APRC_STATE = AR_powerplan['aprc_state']
                    if not APRC_STATE:      #　接近できたかどうか
                        if AR_powerplan["R"] < -0.1 and AR_powerplan["L"] < -0.1:
                            self.move(AR_powerplan["R"],AR_powerplan["L"],0.04)
                            print("Back!")
                            #arm_grasping()
                        else:
                            self.move(AR_powerplan["R"],AR_powerplan["L"],0.02)
                            print("-AR- R:",AR_powerplan["R"],"L:",AR_powerplan["L"])
                        self.rv, self.lv = AR_powerplan["R"],AR_powerplan["L"]
                    else:
                        self.move(0,0,0.2)
                        self.rv, self.lv = 0,0
                        print('state_change')
                        self.estimate_norm = 100000
                        self.done_approach = True
                        if self.connecting_state == 0:
                            self.RED_LED.led_off()
                            self.BLUE_LED.led_on()
                            self.GREEN_LED.led_off()
                            self.arm_release(1650)
                            self.arm_grasping()
                            self.connecting_state += 1
                            self.ar_count = 0
                            self.change_size = 0
                        elif self.connecting_state == 1:
                            self.RED_LED.led_on()
                            self.BLUE_LED.led_off()
                            self.GREEN_LED.led_off()
                            self.arm_release(1650)
                            self.arm_grasping()
                            self.checking_time = time.time()
                            self.connecting_state += 1
                            self.arm.middle()
                            
            else:
                
                if self.aprc_c : #色認識による出力決定するかどうか
                    plan_color = self.cpp.power_planner(self.img,self.connecting_state,self.ar_count)
                    self.aprc_clear = plan_color["Clear"]
                    self.cl_checker = plan_color["Detected_tf"]
                    self.move_clplan = plan_color["move"]
                    self.cl_data = self.cpp.pos
                    if plan_color["Detected_tf"] :
                        #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        if not self.Flag_C:
                            self.starttime_color = time.time()
                            self.Flag_C = True
                            print("keisoku_color")
                            '''
                            Flag(bool値)を使って待機時間の計測を行うための時間計測開始部分
                            '''
                        
                        if self.Flag_C and time.time()-self.starttime_color >= 1.5:
                            '''
                            5秒超えたら入ってくる
                            '''
                            self.vanish_c = 0 #喪失カウントをリセット
                            self.vanish_stuck = 0 #喪失カウントをリセット
                            self.Flag_C = False #フラグをリセット
                            sleep_time = plan_color["w_rate"] * 0.05 + 0.1 ### sleep zikan wo keisan
                            if not self.aprc_clear:
                                self.move(plan_color["R"],plan_color["L"],0.04)
                                print("-Color- R:",plan_color["R"],"L:",plan_color["L"])
                                '''
                                色認識の出力の離散化：出力する時間を0.2秒に
                                '''
                            else:
                                self.pint_count += 1
                                self.change_size += 1
                                self.move(plan_color["R"],plan_color["L"],0.04)
                                # if more than once AR could be seen
                            self.rv, self.lv = plan_color["R"],plan_color["R"]
                            
                    else :
                        if self.vanish_stuck > ct.const.VANISH_BY_STUCK_THRE:
                            self.stuck_detection()
                            self.vanish_stuck -= 40
                        elif self.vanish_c > 10 and not self.aprc_clear:
                            '''
                            数を20に変更
                            '''
                            self.Flag_C = False #色を見つけたら待機できるようにリセット
                            self.Flag_AR = False #AR認識もリセット
                            self.aprc_clear = False #aprc_clearのリセット
                            print("-R:35-")
                            self.move(90,-90,0.03)
                            self.rv, self.lv = 90,-90
                            print('sleeptime : 0.2')
                            self.vanish_c = 0
                            # else:
                                # if self.vanish_c >= 40:
                                    # vanish_sleep = 0.3
                                    # self.vanish_c = 0
                                # else:
                                    # vanish_sleep = 0.1
                                # self.move(40,-40,vanish_sleep)
                                # self.rv, self.lv = 40,-40
                                # print('sleeptime : vanish_sleep')

                        self.vanish_c += 1
                        self.vanish_stuck += 1
                else:
                    if self.vanish_c > 10:
                        self.aprc_c = True #色認識をさせる
                    self.vanish_c += 1
            
            # if self.connecting_state >= 2:  # Finish this state
                # self.arm.up()
                # self.arm.down()
                # self.arm.up()
                # self.RED_LED.led_off()
                # self.BLUE_LED.led_off()
                # self.GREEN_LED.led_off()
                # self.state = 8
                # self.laststate = 8
            return
    
    def arm_grasping(self):
        arm_start, arm_end = 1300, 1300
        if self.connecting_state == 0:
            arm_start = self.arm.down_value
            arm_end = self.arm.up_value
        else:
            arm_atart = 1000
            arm_end = self.arm.middle_value
        # try:
            # arm.setup()
        # except:
            # pass
        self.arm.down()
        self.arm.move(self.arm.down_value)
        time.sleep(3)
        for i in range(arm_start,arm_end,15):
            self.arm.move(i)
            time.sleep(0.1)
        time.sleep(1)
        
    def arm_release(self,pre_arm):
        # try:
            # arm.setup()
        # except:
            # pass
        arm_range = pre_arm - self.arm.down_value
        time.sleep(3)
        for i in range(1,arm_range,20):
            self.arm.move(pre_arm-i)
            time.sleep(0.1)
        time.sleep(1)
    
    def checking(self,frame,connecting_state):
        detected = False
        clear = False
        color_num = 99 # 色変えるならここ変更(cppも)
        self.cpp.AREA_RATIO_THRESHOLD = 0.0000005
            #time.sleep(10.0) # 焼き切り時間用いつか変更する
        # try:
            # arm.setup()
        # except:
            # pass
        #time.sleep(1.0)
        time_clear = False
        if time.time() - self.checking_time > ct.const.MODULE_SEPARATION_TIME_THRE:
            time_clear = True
            pos = self.cpp.find_specific_color(frame,self.cpp.AREA_RATIO_THRESHOLD,self.cpp.LOW_COLOR,self.cpp.HIGH_COLOR,color_num)
            if pos is not None or "7" in self.ar_info.keys() :
                self.cl_data = pos
                #print("pos:",pos[1],"\nTHRESHOLD:",ct.const.CONNECTED_HEIGHT_THRE)
                detected = True
                clear = True
                print('===========\nDone Connection\n===========')
            else:
                self.cl_data = ["none", "none", "none"]
                print('===========\nNO LOOK\n===========')

        return {"clear":clear,"Detected_tf":detected,"Time_clear":time_clear}
    

    def move(self,Vr=0,Vl=0,t=0.1):
        """
		arg:
			Vr : right motor output power. -100 ~ 100   (range v<-40,40<v)
			Vl : left motor output power. -100 ~ 100    (range v<-40,40<v)
			 t : time 
		return:
			none : motor output
		"""
        if Vr>=0:
            if Vr>100:
                Vr=0
            self.MotorR.go(Vr)
        else:
            if Vr<-100:
                Vr=0
            self.MotorR.back(-Vr)
            
        if Vl>=0:
            if Vl>100:
                Vl=0
            self.MotorL.go(Vl)
        else:
            if Vl<-100:
                Vl=0
            self.MotorL.back(-Vl)

        time.sleep(t)

        self.MotorR.stop()
        self.MotorL.stop()

    def running(self):
        self.arm.up()
        dlon = self.goallon - self.lon
        # distance to the goal
        self.goaldis = ct.const.EARTH_RADIUS * arccos(sin(deg2rad(self.lat))*sin(deg2rad(self.goallat)) + cos(deg2rad(self.lat))*cos(deg2rad(self.goallat))*cos(deg2rad(dlon)))
        print(f"Distance to goal: {round(self.goaldis,4)} [km]")

        # angular to the goal (North: 0, South: 180)
        self.goalphi = 90 - rad2deg(arctan2(cos(deg2rad(self.lat))*tan(deg2rad(self.goallat)) - sin(deg2rad(self.lat))*cos(deg2rad(dlon)), sin(deg2rad(dlon))))
        if self.goalphi < 0:
            self.goalphi += 360
        print(self.goalphi)
        
        self.arg_diff = self.goalphi - (self.ex-0)
        if self.arg_diff < 0:
            self.arg_diff += 360
        
        print(f"Argument to goal: {round(self.arg_diff,2)} [deg]")
        
        if self.runningTime == 0:
            self.runningTime = time.time()
            
        # elif time.time() - self.runningTime < 10:
            # print("run")
            
        elif self.goaldis < ct.const.GOAL_DISTANCE_THRE:
            self.MotorR.stop()
            self.MotorL.stop()
            self.goaltime = time.time()-self.runningTime
            self.running_finish = True
            print(f"Goal Time: {self.goaltime}")
            print("GOAAAAAAAAAL!!!!!")
            self.state = 8
            self.laststate = 8
        
        else:
            
            if self.arg_diff <= 180 and self.arg_diff > 20:
                self.MotorR.go(ct.const.RUNNING_MOTOR_VREF-15)
                self.MotorL.go(ct.const.RUNNING_MOTOR_VREF)
                
            elif self.arg_diff > 180 and self.arg_diff < 340:
                self.MotorR.go(ct.const.RUNNING_MOTOR_VREF)
                self.MotorL.go(ct.const.RUNNING_MOTOR_VREF-15)
            
            else:
                self.MotorR.go(ct.const.RUNNING_MOTOR_VREF)
                self.MotorL.go(ct.const.RUNNING_MOTOR_VREF)

    def finish(self):
        if self.finishTime == 0:
            self.finishTime = time.time()
            print("\n",self.startTime)
            print("\nFinished\n")
            self.MotorR.stop()
            self.MotorL.stop()
            GPIO.output(ct.const.SEPARATION_PARA,0) #焼き切りが危ないのでlowにしておく
            GPIO.output(ct.const.SEPARATION_MOD1,0) #焼き切りが危ないのでlowにしておく
            GPIO.output(ct.const.SEPARATION_MOD2,0) #焼き切りが危ないのでlowにしておく
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            self.pc2.stop()
            time.sleep(0.5)
            cv2.destroyAllWindows()
            sys.exit()

    def decide_direction(self,phi):
        if phi >= 20:
            direction_goal = 2
#             print("ゴール方向："+str(direction_goal)+" -> 右に曲がりたい")
        elif phi > -20 and phi < 20:
            direction_goal = 1
#             print("ゴール方向："+str(direction_goal)+" -> 直進したい")
        else:
            direction_goal = 0
#             print("ゴール方向："+str(direction_goal)+" -> 左に曲がりたい")
        return direction_goal
    
     
    def sendLoRa(self): #通信モジュールの送信を行う関数
        datalog = str(self.state)+ ","\
            + str(round(self.lat,5)) + ","\
            + str(round(self.lon,5))
        
        self.lora.sendData(datalog) #データを送信
        
    def stuck_detection(self):
        if (self.bno055.ax**2+self.bno055.ay**2) <= ct.const.STUCK_ACC_THRE**2:
            if self.stuckTime == 0:
                self.stuckTime = time.time()
            
            if self.countstuckLoop > ct.const.STUCK_COUNT_THRE or self.landstate == 1 or self.state == 6: #加速度が閾値以下になるケースがある程度続いたらスタックと判定
                #トルネード実施
                print("stuck")
                self.MotorR.go(ct.const.STUCK_MOTOR_VREF)
                self.MotorL.back(ct.const.STUCK_MOTOR_VREF)
                time.sleep(2)
                self.MotorR.stop()
                self.MotorL.stop()
                self.rv = ct.const.STUCK_MOTOR_VREF
                self.lv = -ct.const.STUCK_MOTOR_VREF
                self.countstuckLoop = 0
                self.stuckTime = 0

            self.countstuckLoop+= 1

        else:
            self.countstuckLoop = 0
            self.stuckTime = 0

    def keyboardinterrupt(self): #キーボードインタラプト入れた場合に発動する関数
        self.MotorR.stop()
        self.MotorL.stop()
        GPIO.output(ct.const.SEPARATION_PARA,0) #焼き切りが危ないのでlowにしておく
        GPIO.output(ct.const.SEPARATION_MOD1,0) #焼き切りが危ないのでlowにしておく
        GPIO.output(ct.const.SEPARATION_MOD2,0) #焼き切りが危ないのでlowにしておく
        self.RED_LED.led_off()
        self.BLUE_LED.led_off()
        self.GREEN_LED.led_off()
        self.pc2.stop()
        time.sleep(0.5)
        cv2.destroyAllWindows()
