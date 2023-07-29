#Last Update 2023/07/28
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
# import Wolvez2023
import constant as ct
from cl_powerplanner import ColorPowerPlanner
from AR_powerplanner import ARPowerPlanner
from bno055 import BNO055
from motor import motor
from gps import GPS
from lora import lora
from led import led
from arm import Arm
from ar_module import Target
from libcam_module import Picam

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
        self.bno055 = BNO055()
        self.MotorL = motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
        self.MotorR = motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN, ct.const.LEFT_MOTOR_VREF_PIN)
        self.gps = GPS()
        self.lora = lora()
        self.arm = Arm(ct.const.SERVO_PIN)
        self.tg = Target()
        self.pc2 = Picam()
        self.cpp = ColorPowerPlanner()
        self.app = ARPowerPlanner()
        self.RED_LED = led(ct.const.RED_LED_PIN)
        self.BLUE_LED = led(ct.const.BLUE_LED_PIN)
        self.GREEN_LED = led(ct.const.GREEN_LED_PIN)
        # self.bno055 = Wolvez2023.BNO055()
        # self.MotorL = Wolvez2023.Motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
        # self.MotorR = Wolvez2023.Motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN, ct.const.LEFT_MOTOR_VREF_PIN)
        # self.gps = Wolvez2023.GPS()
        # self.lora = Wolvez2023.lora()
        # self.arm = Wolvez2023.Arm(ct.const.SERVO_PIN)
        # self.tg = Wolvez2023.Target()
        # self.pc2 = Wolvez2023.Picam()
        # self.cpp = Wolvez2023.ColorPowerPlanner()
        # self.app = Wolvez2023.ARPowerPlanner()
        # self.RED_LED = Wolvez2023.led(ct.const.RED_LED_PIN)
        # self.BLUE_LED = Wolvez2023.led(ct.const.BLUE_LED_PIN)
        # self.GREEN_LED = Wolvez2023.led(ct.const.GREEN_LED_PIN)
        
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
        self.runningTime = 0
        self.finishTime = 0
        self.stuckTime = 0

        # 初期カウンター設定
        self.countFlyLoop = 0
        self.countDropLoop = 0
        self.countstuckLoop = 0
        self.cameraCount = 0
        self.arm_calibCount = 0
        self.avoid_paraCount = 0
        self.ar_count = 0
        self.vanish_c = 0
        self.gpscount = 0
        
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
        self.connecting_state = 1
        
        # state内変数初期設定
        self.estimate_norm = 100000
        self.ar_info = {}
        self.cl_data = [0,0,0]
        self.move_arplan = 'none'
        self.move_clplan = 'none'
        self.goaldis = 0
        self.goalphi = 0
        
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
                  + "rV:"+str(round(self.MotorR.velocity,3)).rjust(6) + ","\
                  + "lV:"+str(round(self.MotorL.velocity,3)).rjust(6) + ","\
                  + "Camera:" + str(self.cameraCount)
        if self.state == 3:
            datalog = datalog + ","\
                 + "Color-Approach:" + str(self.cl_checker) + ","\
                 + "Color-data: x:" + str(self.cl_data[0])+ "y:"+ str(self.cl_data[1]) + "Area:"+ str(self.cl_data[2]) + ","\
                 + "Color-move:" + str(self.move_clplan)
        elif self.state == 6:
           datalog = datalog + ","\
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
                 + "DistanceToGoal:" + str(self.goaldis) + ","\
                 + "ArgumentToGoal:" + str(self.goalphi)+ ","\
                 + "GoalCheck:" + str(self.running_finish)
        
        with open(f'results/{self.startTime}/control_result.txt',"a")  as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(datalog + '\n')

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
                self.state = 7
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
                self.state = 7
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
            else:
                self.MotorR.go(self.plan_color["R"])
                self.MotorL.go(self.plan_color["L"])

                self.stuck_detection()

            if time.time()-self.pre_motorTime > ct.const.LANDING_MOTOR_TIME_THRE: #10秒間モータ回して分離シートから十分離れる
                self.MotorR.stop()
                self.MotorL.stop()
                self.landstate = 2
                print("\n\n=====The arm was calibrated=====\n\n")
                #self.state = 4
                #self.laststate = 4
            
        elif self.landstate == 2: #アームのキャリブレーション
            print("calib arm")
            if self.arm_calibTime == 0:
                self.arm.move(850)
                self.arm.move(1800)
                self.arm.down()
                self.arm_calibTime = time.time()

            if time.time() - self.arm_calibTime < ct.const.ARM_CARIBRATION_THRE:
                self.cameraCount += 1
                self.img = self.pc2.capture(0,self.results_img_dir+f'/{self.cameraCount}')
                detected_img, self.ar_info = self.tg.detect_marker(self.img)
                self.arm.calibration()  # 関数内でキャリブレーションを行う
            else:
                print("\n\n=====The arm was calibrated=====\n\n")
                self.state = 4
                self.laststate = 4

            #if "1" in self.ar_info.keys():
            #    if self.ar_info["1"]["y"] - ct.const.ARM_CALIB_POSITION > 0.5:
            #        self.buff = 0.2
            #   elif self.ar_info["1"]["y"] - ct.const.ARM_CALIB_POSITION < 0.5:
            #        self.buff = -0.2
            #   else:
            #       self.arm_calibCount += 1
  
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
            self.MotorL.go(ct.const.RUNNING_MOTOR_VREF)
            self.pre_motorTime = time.time()
            self.releasingstate = 2
        
        if self.releasingstate == 2:
            if time.time()-self.pre_motorTime > ct.const.RELEASING_MOTOR_TIME_THRE: #5秒間モータ回して一つめのモジュールから十分離れる
                    self.MotorR.stop()
                    self.MotorL.stop()
                    self.modu_sepaTime = 0
                    self.releasingstate = 0
                    self.state = 5
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
                if time.time()-self.modu_sepaTime > ct.const.SEPARATION_TIME_THRE:
                    GPIO.output(ct.const.SEPARATION_MOD2,0) #焼き切りが危ないのでlowにしておく
                    self.releasingstate = 1
        
        if self.releasingstate == 1:
            self.MotorR.go(ct.const.RELEASING_MOTOR_VREF)
            self.MotorL.go(ct.const.RUNNING_MOTOR_VREF)
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
                    self.laststate = 6

    def connecting(self):
        if self.connecting_state == 2:
            SorF = self.checking(self.img,self.connecting_state-1)
            if SorF["Time_clear"]:
                self.state = 8
                self.laststate = 8
        else:
            self.done_approach = False
            if self.connecting_state == 0:
                self.RED_LED.led_off()
                self.BLUE_LED.led_off()
                self.GREEN_LED.led_on()
                self.arm.middle()
            if self.connecting_state == 1:
                self.RED_LED.led_off()
                self.BLUE_LED.led_on()
                self.GREEN_LED.led_off()
                self.arm.up()
            # capture and detect markers
            self.pc2.picam2.set_controls({"AfMode":0,"LensPosition":5})
            self.cameraCount += 1
            self.img = self.pc2.capture(0,self.results_img_dir+f'/{self.cameraCount}')
            self.blk = self.pc2.red2blk(self.img)
            
            detected_img, self.ar_info = self.tg.detect_marker(self.blk)
            self.AR_checker = self.tg.AR_decide(self.ar_info,self.connecting_state)
            self.ar_checker = self.AR_checker["AR"]
            print(self.ar_info)
            if self.AR_checker["AR"]:
                self.vanish_c = 0 #喪失カウントをリセット
                self.aprc_c = False #アプローチの仕方のbool
                self.estimate_norm = self.AR_checker["norm"] #使u これself.いるん？？
                if not self.Flag_AR:
                    print("keisoku_AR")
                    self.starttime_AR = time.time()
                    self.ar_count += 1
                    self.Flag_AR = True
                if self.Flag_AR and time.time()-self.starttime_AR >= 1.0:
                    self.Flag_AR = False #フラグをリセット←これもAR_decideの中で定義しても良いかも
                    AR_powerplan = self.app.ar_powerplanner(self.ar_info,self.connecting_state,self.AR_checker)  #sideを追加
                    self.move_arplan = AR_powerplan["move"]
                    APRC_STATE = AR_powerplan['aprc_state']
                    if not APRC_STATE:      #　接近できたかどうか
                        if AR_powerplan["R"] < -0.1 and AR_powerplan["L"] < -0.1:
                            self.move(AR_powerplan["R"],AR_powerplan["L"],0.05)
                            print("Back!")
                            #arm_grasping()
                        else:
                            self.move(AR_powerplan["R"],AR_powerplan["L"],0.03)
                            print("-AR- R:",AR_powerplan["R"],"L:",AR_powerplan["L"])
                    else:
                        self.move(0,0,0.2)
                        print('state_change')
                        self.estimate_norm = 100000
                        self.done_approach = True
                        if self.connecting_state == 0:
                            self.RED_LED.led_off()
                            self.BLUE_LED.led_on()
                            self.GREEN_LED.led_off()
                            self.arm_grasping()
                            #SorF = self.checking(self.img,self.connecting_state)
                            self.connecting_state += 1
                            self.ar_count = 0
                            #if not SorF["clear"]:
                            #    self.connecting_state -= 1
                        elif self.connecting_state == 1:
                            self.RED_LED.led_on()
                            self.BLUE_LED.led_off()
                            self.GREEN_LED.led_off()
                            self.arm_release()
                            self.checking_time = time.time()
                            SorF = self.checking(self.img,self.connecting_state)
                            self.connecting_state += 1
                            self.arm.up()
                            self.arm.down()
                            self.arm.up()
                            print(f'connect_clear: {SorF["clear"]}')
                            # if not SorF["clear"]:
                                # self.connecting_state -= 2
                            # 焼き切りを待つ時間をここで使いたい（10秒）
                            
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
                        
                        if self.Flag_C and time.time()-self.starttime_color >= 1.0:
                            '''
                            5秒超えたら入ってくる
                            '''
                            self.vanish_c = 0 #喪失カウントをリセット
                            self.Flag_C = False #フラグをリセット
                            sleep_time = plan_color["w_rate"] * 0.05 + 0.1 ### sleep zikan wo keisan
                            if not self.aprc_clear:
                                self.move(plan_color["R"],plan_color["L"],0.04)
                                print("-Color- R:",plan_color["R"],"L:",plan_color["L"])
                                '''
                                色認識の出力の離散化：出力する時間を0.2秒に
                                '''
                                
                            else:
                                self.move(plan_color["R"],plan_color["L"],0.04)
                                # if more than once AR could be seen
                            
                    else :
                        if self.vanish_c > 10 and not self.aprc_clear:
                            '''
                            数を20に変更
                            '''
                            self.Flag_C = False #色を見つけたら待機できるようにリセット
                            self.Flag_AR = False #AR認識もリセット
                            self.aprc_clear = False #aprc_clearのリセット
                            print("-R:35-")
                            if self.estimate_norm > 0.5:
                                self.move(90,-90,0.03)
                                print('sleeptime : 0.2')
                                self.vanish_c = 0
                            else:
                                if self.vanish_c >= 40:
                                    vanish_sleep = 0.3
                                    self.vanish_c = 0
                                else:
                                    vanish_sleep = 0.1
                                self.move(40,-40,vanish_sleep)
                                print('sleeptime : vanish_sleep')

                        self.vanish_c += 1
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
        # try:
            # arm.setup()
        # except:
            # pass
        self.arm.down()
        self.arm.move(1050)
        time.sleep(3)
        for i in range(1050,1500,15):
            self.arm.move(i)
            time.sleep(0.1)
        time.sleep(1)
        
    def arm_release(self):
        # try:
            # arm.setup()
        # except:
            # pass
        time.sleep(3)
        for i in range(1,300,20):
            self.arm.move(1500-i)
            time.sleep(0.1)
        time.sleep(1)
    
    def checking(self,frame,connecting_state):
        detected = False
        clear = False
        if connecting_state == 0:
            color_num = connecting_state
        else:
            color_num = 99 # 色変えるならここ変更(cppも)
            #time.sleep(10.0) # 焼き切り時間用いつか変更する
        # try:
            # arm.setup()
        # except:
            # pass
        #time.sleep(1.0)
        time_clear = False
        if time.time() - self.checking_time > 180:
            time_clear = True
            pos = self.cpp.find_specific_color(frame,self.cpp.AREA_RATIO_THRESHOLD,self.cpp.LOW_COLOR,self.cpp.HIGH_COLOR,color_num)
            if pos is not None:
                self.cl_data = pos
                print("pos:",pos[1],"\nTHRESHOLD:",ct.const.CONNECTED_HEIGHT_THRE)
                detected = True
                if color_num == 0:
                    if pos[1] > ct.const.CONNECTED_HEIGHT_THRE: # パラメータ未調整
                        clear = True
                        time.sleep(2.0)
                        print('===========\nGRASPED\n===========')
                    else:
                        self.arm.middle()
                        time.sleep(1)
                        print('===========\nFAILED\n===========')
                else:
                    clear = True
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
            
        elif time.time() - self.runningTime < 10:
            print("run")
            
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
    
    def safe_or_not(self,lower_risk):
        """
        ・入力:下半分のwindowのリスク行列（3*1または1*3？ここはロバストに作ります）
        ・出力:危険=1、安全=0の(入力と同じ次元)
        """
        self.threshold_risk = np.average(np.array(self.risk_list_below))+2*np.std(np.array(self.risk_list_below))
#         if len(self.risk_list_below)<=100:
#             self.threshold_risk = np.average(np.array(self.risk_list_below))+2*np.std(np.array(self.risk_list_below))
#         else:
#             self.threshold_risk = np.average(np.array(self.risk_list_below[-100:]))+2*np.std(np.array(self.risk_list_below[-100:]))
        
        try:
            self.max_risk=np.max(np.array(self.risk_list_below))
#             if len(self.risk_list_below)<=100:
#                 self.max_risk=np.max(np.array(self.risk_list_below))
#             else:
#                 self.max_risk=np.max(np.array(self.risk_list_below[-100:]))
            
        except Exception:
            self.max_risk=1000
        answer_mtx=np.zeros(3)
        for i, risk_scaler in enumerate(lower_risk):
            if risk_scaler >= self.threshold_risk or risk_scaler >= self.max_risk:
                answer_mtx[i]=1
        return answer_mtx
     
    def sendLoRa(self): #通信モジュールの送信を行う関数
        datalog = str(self.state)+ ","\
            + str(round(self.lat,3)) + ","\
            + str(round(self.lon,3))
        
        self.lora.sendData(datalog) #データを送信
        
    def stuck_detection(self):
        if (self.bno055.ax**2+self.bno055.ay**2) <= ct.const.STUCK_ACC_THRE**2:
            if self.stuckTime == 0:
                self.stuckTime = time.time()
            
            if self.countstuckLoop > ct.const.STUCK_COUNT_THRE: #加速度が閾値以下になるケースがある程度続いたらスタックと判定
                #トルネード実施
                print("stuck")
                self.MotorR.go(ct.const.STUCK_MOTOR_VREF)
                self.MotorL.back(ct.const.STUCK_MOTOR_VREF)
                time.sleep(2)
                self.MotorR.stop()
                self.MotorL.stop()
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
