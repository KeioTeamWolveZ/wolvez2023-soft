#Last Update 2022/07/02
#Author : Toshiki Fukui

from tempfile import TemporaryDirectory
from xml.dom.pulldom import default_bufsize
from pandas import IndexSlice
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
import shutil
# from math import prod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from first_spm import IntoWindow, LearnDict, EvaluateImg
from second_spm import SPM2Open_npz,SPM2Learn,SPM2Evaluate

import constant as ct
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
        GPIO.setup(ct.const.SEPARATION_PIN1,GPIO.OUT) #焼き切り用のピンの設定
        
        # インスタンス生成用      
        self.bno055 = BNO055()
        self.MotorR = motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
        self.MotorL = motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN, ct.const.LEFT_MOTOR_VREF_PIN)
        self.gps = GPS()
        self.lora = lora()
        self.arm = Arm(ct.const.SERVO_PIN)
        self.tg = Target()
        self.pc2 = Picam()
        self.RED_LED = led(ct.const.RED_LED_PIN)
        self.BLUE_LED = led(ct.const.BLUE_LED_PIN)
        self.GREEN_LED = led(ct.const.GREEN_LED_PIN)
        
        #ステート設定用
        self.timer = 0
        self.state = state
        self.landstate = 0
        self.camerastate = 0
        
        #初期パラメータ設定
        self.startTime_time=time.time()
        self.startTime = str(datetime.now())[:19].replace(" ","_").replace(":","-")
        self.preparingTime = 0
        self.flyingTime = 0
        self.droppingTime = 0
        self.landingTime = 0
        self.arm_calibTime = 0
        self.arm_calibCount = 0
        self.runningTime = 0
        self.finishTime = 0
        self.stuckTime = 0
        
        #state管理用変数初期化
        self.gpscount=0
        self.startgps_lon=[]
        self.startgps_lat=[]
        
        #ステート管理用変数設定
        self.countFlyLoop = 0
        self.countDropLoop = 0
        self.countstuckLoop = 0

        self.dict_list = {}
        self.goallat = ct.const.GPS_GOAL_LAT
        self.goallon = ct.const.GPS_GOAL_LON
        self.saveDir = "results"
        self.mkdir()
        self.mkfile()
        self.mvfile()

    def mkdir(self): #フォルダ作成部分
        folder_paths =[f"results/{self.startTime}",
                       f"results/{self.startTime}/camera_result",
                       f"results/{self.startTime}/camera_result/planning",
                       f"results/{self.startTime}/camera_result/planning/learn{self.learncount}",
                       f"results/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_npz",
                       f"results/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_pics"]
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
                  + "Camera:" + str(self.camerastate)

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
                  + "Camera:" + str(self.camerastate)
        
        with open(f'results/{self.startTime}/control_result.txt',"a")  as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(datalog + '\n')

    def writeSparseData(self,risk): #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる   
        if self.state == 6:
            datalog_sparse =  str(self.timer) + ","\
                    + "Time:"+str(self.gps.Time) + ","\
                    + "Lat:"+str(self.gps.Lat).rjust(6) + ","\
                    + "Lng:"+str(self.gps.Lon).rjust(6) + ","\
                    + "Goal Distance:"+str(self.gps.gpsdis).rjust(6) + ","\
                    + "Goal Angle:"+str(self.gps.gpsdegrees).rjust(6) + ",\n"\
                    + "    "\
                    +"q:"+str(self.bno055.ex).rjust(6) + ","\
                    + "Risk:"+str(np.array(self.risk).reshape(1,-1)).rjust(6) + ","\
                    + "threadshold_risk:"+str(self.threshold_risk).rjust(6) + ","\
                    + "max_risk:"+str(self.max_risk).rjust(6)+","\
                    + "boolean_risk:"+str(self.boolean_risk).rjust(6)+","\
                    + "    "\
                    + "Plan:"+str(self.plan_str) + ","\
                    + "rV:"+str(round(self.MotorR.velocity,3)).rjust(6) + ","\
                    + "lV:"+str(round(self.MotorL.velocity,3)).rjust(6) + ","\


            with open(f'results/{self.startTime}/planning_result.txt',"a")  as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
                test.write(datalog_sparse + '\n')
                print("### SPARSE LOG ###",datalog_sparse)


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
        self.lora.sendDevice.setup_lora()
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
        
        self.writeData() #txtファイルへのログの保存
    
        if not self.state == 1: #preparingのときは電波を発しない
            self.sendLoRa()

    def preparing(self): #時間が立ったら移行
        if self.preparingTime == 0:
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
        if self.landingTime == 0: #時刻を取得してLEDをステートに合わせて光らせる
            self.landingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
            
        if not self.landingTime == 0:
            #焼き切りによるパラ分離
            if self.landstate == 0:
                GPIO.output(ct.const.SEPARATION_PIN,1) #電圧をHIGHにして焼き切りを行う
                if time.time()-self.landingTime > ct.const.SEPARATION_TIME_THRE:
                    GPIO.output(ct.const.SEPARATION_PIN,0) #焼き切りが危ないのでlowにしておく
                    self.landstate = 1
            
            elif self.landstate == 1: #アームのキャリブレーション
                if self.arm_calibTime == 0:
                    self.arm.down()
                    self.arm_calibTime = time.time()

                if time.time() - self.arm_calibTime < ct.const.ARM_CARIBRATION_THRE:
                    self.img = self.pc2.capture(1)
                    self.img = self.tg.addSpace(self.img)
                    detected_img, ar_info = self.tg.detect_marker(self.img)
                else:
                    self.landstate = 2
                    print("\nThe arm was not calibrated")
                    self.pre_motorTime = time.time()

                if "1" in ar_info.keys():
                    if ar_info["1"]["y"] - ct.const.ARM_CALIB_POSITION > 0.1:
                        self.buff = 0.2
                    elif ar_info["1"]["y"] - ct.const.ARM_CALIB_POSITION < 0.1:
                        self.buff = -0.2
                    else:
            
            #パラシュートの色を検知して離脱
            elif self.landstate == 2:
                self.MotorR.go(ct.const.LANDING_MOTOR_VREF)
                self.MotorL.go(ct.const.LANDING_MOTOR_VREF)

                self.stuck_detection()

                if time.time()-self.pre_motorTime > ct.const.LANDING_MOTOR_TIME_THRE: #5秒間モータ回して分離シートから十分離れる
                    self.MotorR.stop()
                    self.MotorL.stop()
                    self.state = 4
                    self.laststate = 4
  
    def finish(self):
        if self.finishTime == 0:
            self.finishTime = time.time()
            print("Finished")
            self.MotorR.stop()
            self.MotorL.stop()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
            self.cap.release()
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
        datalog = str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon)

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
        GPIO.output(ct.const.SEPARATION_PIN,0) #焼き切りが危ないのでlowにしておく
        self.RED_LED.led_off()
        self.BLUE_LED.led_off()
        self.GREEN_LED.led_off()
        self.cap.release()
        time.sleep(0.5)
        cv2.destroyAllWindows()