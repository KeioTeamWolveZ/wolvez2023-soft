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

from bno055 import BNO055
from motor import motor
from gps import GPS
from lora import lora
from led import led
import constant as ct

"""
ステート説明
0. preparing()  準備ステート。センサ系の準備。一定時間以上経過したらステート移行。
1. flying()     放出準備ステート。フライトピンが接続されている状態（＝ボイド缶に収納されている）。フライトピンが外れたらステート移行。
2. droping()    降下&着陸判定ステート。加速度センサの値が一定値以下の状態が一定時間続いたら着陸と判定しステート移行。
3. landing()    分離ステート。分離シートの焼ききりによる分離、モータ回転による分離シートからの離脱を行ったらステート移行。
4. spm_first()  第1段階スパースモデリングステート。最初に撮影した画像に特徴処理(10種類:RGB,r,g,b,rb,rg,gb,edge,edge enphasis, HSV)を行い、
                それぞれで辞書作成。再構成した際の元画像との差分のヒストグラムから特徴量（6種類: 平均,分散,中央値,最頻値,歪度,尖度）を抽出。
5. spm_second() 第2段階スパースモデリングステート。第一段階で獲得した特徴処理に対する特徴量（1ウィンドウ60個の特徴量、全体で360個の特徴量）から
                重要な特徴量を抽出。危険度の算出まで可能になる。
6. running()    経路計画&走行ステート。ステート5まで獲得したモデルで危険度を逐次算出しながら経路を計画。計画した経路を走行。
7. finish()     終了ステート
"""

class Cansat():
    def __init__(self,state):
        # GPIO設定
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM) #GPIOの設定
        GPIO.setup(ct.const.FLIGHTPIN_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP) #フライトピン用。プルアップを有効化
        GPIO.setup(ct.const.SEPARATION_PIN,GPIO.OUT) #焼き切り用のピンの設定
        
        # インスタンス生成用      
        self.bno055 = BNO055()
        self.MotorR = motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
        self.MotorL = motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN, ct.const.LEFT_MOTOR_VREF_PIN)
        self.gps = GPS()
        self.lora = lora()
        self.RED_LED = led(ct.const.RED_LED_PIN)
        self.BLUE_LED = led(ct.const.BLUE_LED_PIN)
        self.GREEN_LED = led(ct.const.GREEN_LED_PIN)
        
        #ステート設定用
        self.timer = 0
        self.state = state
        self.landstate = 0
        self.camerastate = 0
        self.camerafirst = 0
        self.learn_state = True
        
        #初期パラメータ設定
        self.startTime_time=time.time()
        self.startTime = str(datetime.now())[:19].replace(" ","_").replace(":","-")
        self.preparingTime = 0
        self.flyingTime = 0
        self.droppingTime = 0
        self.landingTime = 0
        self.spmfirstTime = 0
        self.spmsecondTime = 0
        self.runningTime = 0
        self.finishTime = 0
        self.stuckTime = 0
        
        #state管理用変数初期化
        self.gpscount=0
        self.startgps_lon=[]
        self.startgps_lat=[]
        self.risk_list = []
        self.risk_list_below = []
        self.max_risk = -10000000
        self.risk = [-100,-100,-100,-100,-100,-100]
#         self.risk = [[0,0,0],[0,0,0]]
        self.plan_str = "not defined"
        
        #ステート管理用変数設定
        self.countFlyLoop = 0
        self.countDropLoop = 0
        self.learncount = 1
        self.firstlearnimgcount = 0
        self.firstevalimgcount = 0
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
                       f"results/{self.startTime}/camera_result/first_spm",
                       f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount}",
                       f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount}/evaluate",
                       f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount}/processed",
                       f"results/{self.startTime}/camera_result/second_spm",
                       f"results/{self.startTime}/camera_result/second_spm/learn{self.learncount}",
                       f"results/{self.startTime}/camera_result/planning",
                       f"results/{self.startTime}/camera_result/planning/learn{self.learncount}",
                       f"results/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_npz",
                       f"results/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_pics"]

        for folder_path in folder_paths:
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

    def mkfile(self):
        control_path = open(f'results/{self.startTime}/control_result.txt', 'w')
        control_path.close()
        planning_path = open(f'results/{self.startTime}/planning_result.txt', 'w')
        planning_path.close()

    def mvfile(self):
        pre_data = sorted(glob("../../pre_data/*"))
        dest_dir = f"results/{self.startTime}/camera_result/second_spm/learn{self.learncount}"
        for file in pre_data:
            shutil.copy2(file, dest_dir)
    
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
        if self.state == 0: #センサ系の準備を行う段階。時間経過でステート移行
            self.preparing()
        elif self.state == 1: #放出を検知する段階。フライトピンが抜けたらステート移行
            self.flying()
        elif self.state == 2: #着陸判定する段階。加速度の値が一定値以下になったら着陸したと判定してステート移行
            self.dropping()
        elif self.state == 3: #焼き切り&パラシュートから離脱したらステート移行
            self.landing()
        elif self.state == 4: #スパースモデリング第一段階
            self.spm_first(ct.const.SPMFIRST_PIC_COUNT)
        elif self.state == 5: #スパースモデリング第二段階
            self.model_master,self.scaler_master,self.feature_names = self.spm_second()
        elif self.state == 6: #経路計画&走行実施
            self.running(self.model_master,self.scaler_master,self.feature_names)
        # elif self.state == 7:
        #     self.re_learning()
        elif self.state == 7:#終了
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

    def landing(self): #着陸判定ステート。焼き切り&分離シートからの離脱が必要
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
                    self.pre_motorTime = time.time()
            
            #分離シート離脱
            elif self.landstate == 1:
                self.MotorR.go(ct.const.LANDING_MOTOR_VREF)
                self.MotorL.go(ct.const.LANDING_MOTOR_VREF)

                self.stuck_detection()

                if time.time()-self.pre_motorTime > ct.const.LANDING_MOTOR_TIME_THRE: #5秒間モータ回して分離シートから十分離れる
                    self.MotorR.stop()
                    self.MotorL.stop()
                    self.state = 4
                    self.laststate = 4

    def spm_first(self, PIC_COUNT:int=1, relearning:dict=dict(relearn_state=False,f1=ct.const.f1,f3=ct.const.f3)): #ステート4。スパースモデリング第一段階実施。
        if self.spmfirstTime == 0: #時刻を取得してLEDをステートに合わせて光らせる
            self.spmfirstTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()
        '''
        CHECK POINT
        ---
        MUST READ:
            1: This IntelliSence
            2: line 331~359 for learn state
            3: line 393~425 for evaluate state
        ------
        EXPLANATION
        ---
        args:
            PIC_COUNT (int) : number of taking pics
            relearning (dict) : dict of informations for relearning; relearn_state (bool), f1 (int) for number not should be counted as stack-pos, f3 (int) for number should be counted include f1
        
        flow:
            First Learning:
                1: PIC_COUNT=1, (global)learn_state=True
                2: PIC_COUNT=50?, (global)learn_state=False
            ReLearning:
                3: PIC_COUNT=1, (global)learn_state=True, relearning={'relearn_state':True, 'f1':int, 'f3':int}\\
                4: PIC_COUNT=50?, (global)learn_state=False, relearning={'relearn_state':True, 'f1':int, 'f3':int}
        
        output:
            New npzs will be in the current "learncount" folder
        '''
        start_time = time.time() #学習用時間計測。学習開始時間
        
        #保存時のファイル名指定（現在は時間）
        now=str(datetime.now())[:19].replace(" ","_").replace(":","-")

        Save = True
        
        # Path that img will be read
        #importPath = path.replace("\\", "/")
        
        # This will change such as datetime
        # print("CURRENT FRAME: "+str(re.findall(".*/frame_(.*).jpg", importPath)[0]))
        
        iw_shape = (2, 3)  #ウィンドウのシェイプ
        D: any
        ksvd: any  # 最初に指定しないと怒られちゃうから
        feature_values = {}

        if self.learn_state:
            print(f"=====LEARNING PHASE{self.learncount}=====")
        else:
            print(f"=====EVALUATING PHASE{self.learncount}=====")
        
        if self.learn_state: #学習モデル獲得     
            if relearning['relearn_state']:  # 再学習に用いる画像パスの指定
                # 一つ前のlearncountファイルの-f3枚目を指定
                try:
                    importPath = sorted(glob(f"results/{self.startTime}/camera_result/planning/learn{self.learncount-1}/planning_pics/planningimg*.jpg"))[-relearning['f3']]
                except IndexError:
                    # ここで学習枚数足りなかったら動作指定（あきらめて１回目と同じ動きするのか、再学習をあきらめるか）
                    print('There are not enough number of pics for ReLearning.')
                    # relearning['relearn_state'] = False  # 再学習用に画像を1枚
            
            if not relearning['relearn_state']:
                #学習用画像を一枚撮影
                '''
                再学習の段階でcamerafirstの値を指定することで
                辞書再作成用の画像撮影の有無を決定
                '''
                if self.camerafirst == 0:
                    self.cap = cv2.VideoCapture(0)
                    ret, firstimg = self.cap.read()
                    cv2.imwrite(f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount}/firstimg{self.firstlearnimgcount}.jpg",firstimg)
                    self.camerastate = "captured!"
                    self.sensor()
                    self.camerastate = 0
                    self.firstlearnimgcount += 1
                    self.camerafirst = 1
                elif self.camerafirst == 2:
                    '''
                    再撮影をする場合はここに記載
                    '''
                
                importPath = f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount}/firstimg{self.firstlearnimgcount-1}.jpg"
            
            processed_Dir = f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount}/processed"
            iw = IntoWindow(importPath, processed_Dir, Save) #画像の特徴抽出のインスタンス生成
            self.img=cv2.imread(importPath, 1)
            self.img = self.img[int(0.25*self.img.shape[0]):int(0.75*self.img.shape[0])]
            cv2.imwrite(importPath, self.img)
            
            # processing img
            fmg_list = iw.feature_img(frame_num=now) #特徴抽出。リストに特徴画像が入る 
            for fmg in fmg_list:#それぞれの特徴画像に対して処理
                # breakout by windows
                iw_list, window_size = iw.breakout(cv2.imread(fmg, cv2.IMREAD_GRAYSCALE)) #ブレイクアウト
                feature_name = str(re.findall(self.saveDir + f"/{self.startTime}/camera_result/first_spm/learn{self.learncount}/processed/(.*)_.*_", fmg)[0])
                # print("FEATURED BY: ",feature_name)

                for win in range(int(np.prod(iw_shape))): #それぞれのウィンドウに対して学習を実施
                    if win+1 == int((iw_shape[0]-1)*iw_shape[1]) + int(iw_shape[1]/2) + 1:
                        ld = LearnDict(iw_list[win])
                        D, ksvd = ld.generate() #辞書獲得
                        self.dict_list[feature_name] = [D, ksvd]
                        save_name = self.saveDir + f"/learn{self.learncount}/learnimg/{feature_name}_part_{win+1}_{now}.jpg"
                        # cv2.imwrite(save_name, iw_list[win])
            self.learn_state = False

        else:# PIC_COUNT枚撮影
            if self.state == 4:  # 再学習時にステート操作が必要なら追記
                self.spm_f_eval(PIC_COUNT=50, now=now, iw_shape=iw_shape, relearning=relearning) #第2段階用の画像を撮影
                self.state = 5
                self.laststate = 5
            else:
                self.spm_f_eval(PIC_COUNT=PIC_COUNT, now=now, iw_shape=iw_shape, relearning=relearning) #第2段階用の画像を撮影

    def spm_f_eval(self, PIC_COUNT=1, now="TEST", iw_shape=(2,3),feature_names=None, relearning:dict=dict(relearn_state=False,f1=ct.const.f1,f3=ct.const.f3)):#第一段階学習&評価。npzファイル作成が目的
        if relearning['relearn_state']:
            try:
                second_img_paths = sorted(glob(f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount-1}/evaluate/evaluateimg*.jpg"))[-relearning['f3']+1:-relearning['f1']]
            except IndexError:
                # ここで学習枚数足りなかったら動作指定（あきらめて１回目と同じ動きするのか、再学習をあきらめるか）
                print('There are not enough number of pics for ReLearning.')
                # relearning['relearn_state'] = False  # 再学習用に画像を1枚
        
        if not relearning['relearn_state']:
        # self.cap = cv2.VideoCapture(0)
            for i in range(PIC_COUNT):
                try:
                    ret,self.secondimg = self.cap.read()
                    print("done:",i)
                except:
                    pass
                if self.state == 4:
                    save_file = f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount}/evaluate/evaluateimg{time.time():.2f}.jpg"
                elif self.state == 6:
                    save_file = f"results/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_pics/planningimg{time.time():.2f}.jpg"

                cv2.imwrite(save_file,self.secondimg)
                self.firstevalimgcount += 1
                
                if self.state == 4:
                    # self.MotorR.go(74)#走行
                    # self.MotorL.go(70)#走行
                    # # self.stuck_detection()
                    # time.sleep(0.1)
                    # self.MotorR.stop()
                    # self.MotorL.stop()
                    # if i%10 == 0: #10枚撮影する毎にセンサの値取得
                    #     self.camerastate = "captured!"
                    #     self.sensor()
                    #     self.camerastate = 0
                    # state4の学習時にもBNOベースで走行
                    self.sensor()
                    self.planning(np.array([0,0,0,0,0,0]))
                    self.stuck_detection()#ここは注意
#                     print(f"{fmg_list.index(fmg)} fmg evaluated")
                
            if not PIC_COUNT == 1:
                second_img_paths = sorted(glob(f"results/{self.startTime}/camera_result/first_spm/learn{self.learncount}/evaluate/evaluateimg*.jpg"))
            else:
                second_img_paths = [save_file]
        
        for importPath in second_img_paths:
            self.GREEN_LED.led_on()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
        
            feature_values = {}

            default_names = ["normalRGB","enphasis","edge","hsv","red","blue","green","purple","emerald","yellow"]
            for keys in default_names:
                feature_values[keys] = {}
            
            self.tempDir = TemporaryDirectory()
            tempDir_name = self.tempDir.name
            
            iw = IntoWindow(importPath, tempDir_name, False) #画像の特徴抽出のインスタンス生成
            self.img=cv2.imread(importPath, 1)
            self.img = self.img[int(0.25*self.img.shape[0]):int(0.75*self.img.shape[0])]
            cv2.imwrite(importPath, self.img)
            
            #if self.state == 4: #ステートが4の場合はセンサの値取得
                #self.sensor()
            print(feature_names)
            if feature_names == None: #第一段階学習モード
                self.camerastate = "captured!"
                fmg_list = iw.feature_img(frame_num=now,feature_names=feature_names) #特徴抽出。リストに特徴画像が入る
                
                for fmg in fmg_list:#それぞれの特徴画像に対して処理
                    iw_list, window_size = iw.breakout(cv2.imread(fmg,cv2.IMREAD_GRAYSCALE)) #ブレイクアウト
                    feature_name = str(re.findall(tempDir_name + f"/(.*)_.*_", fmg)[0])
                    
                    # print("FEATURED BY: ",feature_name)
                    
                    D, ksvd = self.dict_list[feature_name]
                    for win in range(int(np.prod(iw_shape))): #それぞれのウィンドウに対して評価を実施

                        # win_1~3は特徴量算出を行わない
                        if win not in [0,1,2]:
                            ei = EvaluateImg(iw_list[win])
                            img_rec = ei.reconstruct(D, ksvd, window_size)
                            saveName = self.saveDir + f"/{self.startTime}/camera_result/first_spm/learn{self.learncount}/processed/difference"
                            if not os.path.exists(saveName):
                                os.mkdir(saveName)
                            saveName = self.saveDir + f"/{self.startTime}/camera_result/first_spm/learn{self.learncount}/processed/difference/{now}"
                            if not os.path.exists(saveName):
                                os.mkdir(saveName)
                            ave, med, var, mode, kurt, skew = ei.evaluate(iw_list[win], img_rec, win+1, feature_name, now, self.saveDir)
                        else :
                            ave, med, var, mode, kurt, skew = 0, 0, 0, 0, 0, 0

                        feature_values[feature_name][f'win_{win+1}'] = {}
                        feature_values[feature_name][f'win_{win+1}']["var"] = ave  # 平均値
                        feature_values[feature_name][f'win_{win+1}']["med"] = med  # 中央値
                        feature_values[feature_name][f'win_{win+1}']["ave"] = var  # 分散値
                        feature_values[feature_name][f'win_{win+1}']["mode"] = mode  # 最頻値
                        feature_values[feature_name][f'win_{win+1}']["kurt"] = kurt  # 尖度
                        feature_values[feature_name][f'win_{win+1}']["skew"] = skew  # 歪度
                
                self.camerastate = 0
                       
            else: #第一段階評価モード。runningで使うための部 # ここ変える
                feature_list = ["normalRGB","enphasis","edge","hsv","red","blue","green","purple","emerald","yellow"]
                features = []
                
                for feature in feature_names:# windowgoto
                    features = features + feature
#                     print("feature_names:",feature_names)
                features = set(features)
                features = list(features) #windownosaishouchi
                print("features:",features)
                fmg_list = iw.feature_img(frame_num=now,feature_names=features) # 特徴抽出。リストに特徴画像が入る

                for fmg in fmg_list: #それぞれの特徴画像に対して処理
                    iw_list, window_size = iw.breakout(cv2.imread(fmg,cv2.IMREAD_GRAYSCALE)) # ブレイクアウトにより画像を6分割
                    feature_name = str(re.findall(tempDir_name + f"/(.*)_.*_", fmg)[0]) # 特徴処理のみ抽出
                    # print("FEATURED BY: ",feature_name)
                    for win in range(int(np.prod(iw_shape))): #それぞれのウィンドウに対して評価を実施
                        if feature_name in feature_names[win] and win not in [0,1,2]: #ウィンドウに含まれいていた場合
                            D, ksvd = self.dict_list[feature_name]
                            ei = EvaluateImg(iw_list[win])
                            img_rec = ei.reconstruct(D, ksvd, window_size)
                            saveName = self.saveDir + f"/{self.startTime}/camera_result/first_spm/learn{self.learncount}/processed/difference"
    #                         if not os.path.exists(saveName):
    #                             os.mkdir(saveName)
    #                         saveName = self.saveDir + f"/camera_result/first_spm/learn{self.learncount}/processed/difference/{now}"
    #                         if not os.path.exists(saveName):
    #                             os.mkdir(saveName)
                            ave, med, var, mode, kurt, skew = ei.evaluate(iw_list[win], img_rec, win+1, feature_name, now, self.saveDir)

                        else:
                            ave, med, var, mode, kurt, skew = 0, 0, 0, 0, 0, 0


                        feature_values[feature_name][f'win_{win+1}'] = {}
                        feature_values[feature_name][f'win_{win+1}']["var"] = ave  # 平均値
                        feature_values[feature_name][f'win_{win+1}']["med"] = med  # 中央値
                        feature_values[feature_name][f'win_{win+1}']["ave"] = var  # 分散値
                        feature_values[feature_name][f'win_{win+1}']["mode"] = mode  # 最頻値
                        feature_values[feature_name][f'win_{win+1}']["kurt"] = kurt  # 尖度
                        feature_values[feature_name][f'win_{win+1}']["skew"] = skew  # 歪度
                                
                    for feature_name in feature_list:
                        if feature_name not in features:
                            for win in range(int(np.prod(iw_shape))): #それぞれのウィンドウに対して評価を実施
                                feature_values[feature_name][f'win_{win+1}'] = {}
                                feature_values[feature_name][f'win_{win+1}']["var"] = 0  # 平均値
                                feature_values[feature_name][f'win_{win+1}']["med"] = 0  # 中央値
                                feature_values[feature_name][f'win_{win+1}']["ave"] = 0  # 分散値
                                feature_values[feature_name][f'win_{win+1}']["mode"] = 0  # 最頻値
                                feature_values[feature_name][f'win_{win+1}']["kurt"] = 0  # 尖度
                                feature_values[feature_name][f'win_{win+1}']["skew"] = 0  # 歪度

                    if fmg != fmg_list[-1] and type(self.risk) == np.ndarray:
                        self.sensor()
                        self.planning(self.risk)
                        self.stuck_detection()#ここは注意
#                     print(f"{fmg_list.index(fmg)} fmg evaluated")
                    
            self.BLUE_LED.led_on()
            # npzファイル形式で計算結果保存
            if self.state == 4:
                # self.savenpz_dir = "/home/pi/Desktop/wolvez2022/pre_data/"
                self.savenpz_dir = self.saveDir + f"/{self.startTime}/camera_result/second_spm/learn{self.learncount}/"
            elif self.state == 6:
                self.savenpz_dir = self.saveDir + f"/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_npz/"
            
            # 保存時のファイル名指定（現在は時間）
            now=str(datetime.now())[:21].replace(" ","_").replace(":","-")
#             print("feature_values:",feature_values)
            # print("shape:",len(feature_values))
            np.savez_compressed(self.savenpz_dir + now,array_1=np.array([feature_values])) #npzファイル作成
            self.tempDir.cleanup()
        self.GREEN_LED.led_on()
        self.RED_LED.led_on()
        self.BLUE_LED.led_off()
    
    def spm_second(self): #スパースモデリング第二段階実施
        if self.spmsecondTime == 0: #時刻を取得してLEDをステートに合わせて光らせる
            self.spmfirstTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
            
        npz_dir = f"results/{self.startTime}/camera_result/second_spm/learn{self.learncount}/*"
        train_npz = sorted(glob(npz_dir))
        spm2_prepare = SPM2Open_npz()
        data_list_all_win,label_list_all_win = spm2_prepare.unpack(train_npz)
        spm2_learn = SPM2Learn()

        # ウィンドウによってスタックと教示する時間帯を変えず、一括とする場合
        f1 = ct.const.f1
        f2 = ct.const.f2

        # ウィンドウによってスタックすると教示する時間帯を変える場合はnp.arrayを定義
        f1f2_array_window_custom = None
        """
            f1f2_array_window_custom=np.array([[12., 18.],
                [12., 18.],
                [12., 18.],
                [12., 18.],
                [12., 18.],
                [12, 18.]])
            「stackした」と学習させるフレームの指定方法
            1. 全ウィンドウで一斉にラベリングする場合
                Learnの引数でstack_appearおよびstack_disappearを[s]で指定する。
            2. ウィンドウごとに個別にラベリングする場合
            f1f2_array_window_custom=np.array(
                [
                    [win_1_f1,win_1_stack_f2],
                    [win_2_f1,win_2_stack_f2],
                    ...
                    [win_6_f1,win_6_stack_f2],
                ]
            )
            t[s]で入力すること。
        """
        spm2_learn.start(data_list_all_win,label_list_all_win,f1+ct.const.SPMFIRST_PIC_COUNT, f2+ct.const.SPMFIRST_PIC_COUNT,alpha=5.0,f1f2_array_window_custom=f1f2_array_window_custom) #どっちかは外すのがいいのか
        model_master,label_list_all_win,scaler_master=spm2_learn.get_data()
        nonzero_w, nonzero_w_label, nonzero_w_num = spm2_learn.get_nonzero_w()
#         print("feature_names",np.array(nonzero_w_label,dtype=object).shape)
        feature_names = nonzero_w_label
        
        if self.state == 5:
            print("===== SPARSE MODEL =====")
            print(feature_names)
        
        """
            model_master: 各ウィンドウを学習したモデル（俗にいう"model.predict()"とかの"model.predict()"とかのmodelに相当するのがリストで入ってる）
            label_list_all_win: 重み行列の各成分を、その意味（ex.window_1のrgb画像のaverage）の説明で書き換えた配列
            scaler_master: 各ウィンドウを標準化した時のモデル（scaler.transform()の"scaler"に相当するのがリストで入って）
            feature_names: 特徴処理の名前をリストに格納
        """
        
        self.state = 6
        self.laststate = 6
        return model_master,scaler_master,feature_names

    def running(self,model_master,scaler_master,feature_names): #経路計画&走行
        time_pre = time.time()
        planning_dir = f"results/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_npz/*"
        planning_npz = sorted(glob(planning_dir))
        
        #保存時のファイル名指定（現在は時間）
        now=str(datetime.now())[:19].replace(" ","_").replace(":","-")
        
        self.spm_f_eval(now = now,feature_names = feature_names) #第一段階と同様の処理実施。特徴処理を行なってnpzファイル作成
        print("time1:",time.time()-time_pre)
        if self.runningTime == 0:
            self.runningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
        else:
            SPM2_predict_prepare = SPM2Open_npz()
            print("ROI start")
            print(planning_npz)
            print("ROI ended")
            test_data_list_all_win,test_label_list_all_win = SPM2_predict_prepare.unpack([planning_npz[-1]]) #作成したnpzファイルを取得
            spm2_predict = SPM2Evaluate()
            spm2_predict.start(model_master,test_data_list_all_win,test_label_list_all_win,scaler_master,self.risk_list) #第二段階の評価を実施
            self.risk = spm2_predict.get_score()
            self.risk = np.array([self.risk[i][0][0] for i in range(6)])
            self.risk_list.append(self.risk)
            self.risk_list_below.append(self.risk[3:])
#             self.risk = np.array(self.risk).reshape(2,3) #win1~win6の危険度マップ作成
            
            if len(self.risk_list) >= ct.const.MOVING_AVERAGE:
                self.risk_list = self.risk_list[1:]
            
            print("===== Risk Map =====")
            # for i in range(self.risk.shape[0]):
            #     for j in range(self.risk.shape[1]):
            #         if self.risk[i][j] >= 100:
            #             self.risk[i][j] = 100
            #         elif self.risk[i][j] <= -100:
            #             self.risk[i][j] = -100
            print(np.round(self.risk))
    #         # 走行
            self.sensor()
            self.planning(self.risk)
            self.stuck_detection()#ここは注意
            time_now = time.time()
            print("calc time:",time_now-time_pre)
            if self.gps.gpsdis <= ct.const.FINISH_DIS_THRE:
                self.state = 7
                self.laststate = 7
                
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
    
    def planning(self,risk):
        self.gps.vincenty_inverse(float(self.gps.Lat),float(self.gps.Lon),self.goallat,self.goallon) #距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
        self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))
        self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
        theta_goal = self.gps.gpsdegrees
        # phi = theta_goal-self.bno055.ex
        phi = - self.bno055.ex  # 雨用にbnoの値だけをとってくる
        
        if phi < -180:
            phi += 360
        elif phi > 180:
            phi -= 360
#         print("theta_goal:",theta_goal,"ex:",self.bno055.ex)
        print("distance:", self.gps.gpsdis)

        dir_run = self.calc_dir(risk,phi)
        print(f"###Plan:{self.plan_str}, risk:{risk}, boolean_risk:{self.boolean_risk}")
        if dir_run == 0:
#             print("Left")
            self.MotorR.go(70)
            self.MotorL.go(50)
        elif dir_run == 1:
#             print("Straight")
            self.MotorR.go(60)
            self.MotorL.go(60)
        elif dir_run == 2:
#             print("Right")
            self.MotorR.go(50)
            self.MotorL.go(70)
        elif dir_run == 3:
#             print("Stop")
            self.MotorR.back(60)
            self.MotorL.go(60)
            time.sleep(0.5)
            self.MotorR.go(60)
            self.MotorL.go(60)
            time.sleep(1)
        
        self.writeSparseData(risk)

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

    def calc_dir(self,risk,phi):

        lower_risk = [risk[i] for i in range(3,6)]
        
        
        self.boolean_risk = list(self.safe_or_not(lower_risk))
        
        direction_goal = self.decide_direction(phi)
        dir_run = 0
        if self.boolean_risk == [0, 0, 0]:
            self.plan_str = "to goal"
            dir_run = direction_goal
        elif self.boolean_risk == [1, 0, 0]:
            self.plan_str = "avoid to right"
            dir_run = 2
        elif self.boolean_risk == [0, 1, 0]:
            if lower_risk[0] > lower_risk[2]:
                self.plan_str = "avoid to right"
                dir_run = 2
            else:
                self.plan_str = "avoid to left"
                dir_run = 0
        elif self.boolean_risk == [0, 0, 1]:
            self.plan_str = "avoid to left"
            dir_run = 0
        elif self.boolean_risk == [1, 1, 0]:
            self.plan_str = "avoid to right"
            dir_run = 2
        elif self.boolean_risk == [1, 0, 1]:
            self.plan_str = "turning to avoid"
            dir_run = 3
        elif self.boolean_risk == [0, 1, 1]:
            self.plan_str = "avoid to left"
            dir_run = 0
        elif self.boolean_risk == [1, 1, 1]:
            self.plan_str = "turning to avoid"
            dir_run = 3
                        
        return dir_run
            
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