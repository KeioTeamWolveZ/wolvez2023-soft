# -*- coding: utf-8 -*-
"""
Keio Wolve'Z cansat2021
mission function
Author Hikaru Kimura
last update:2021/8/04

"""

#ライブラリの読み込み
import time
import RPi.GPIO as GPIO
import sys
import numpy as np
import datetime
import os
import csv
import math


#クラス読み込み
import constant as ct
import gps
import motor
import estimation
import radio
import bno055
import led
import servomotor

class Cansat(object):
    
    def __init__(self):
        GPIO.setwarnings(False)
        #オブジェクトの生成
        self.rightmotor = motor.motor(ct.const.RIGHT_MOTOR_IN1_PIN,ct.const.RIGHT_MOTOR_IN2_PIN,ct.const.RIGHT_MOTOR_VREF_PIN)
        self.leftmotor = motor.motor(ct.const.LEFT_MOTOR_IN1_PIN,ct.const.LEFT_MOTOR_IN2_PIN,ct.const.LEFT_MOTOR_VREF_PIN)
        self.encoder = estimation.estimation(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.RIGHT_MOTOR_ENCODER_B_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_B_PIN)

        self.servomotor = servomotor.servomotor(ct.const.SERVOMOTOR_PIN)
        self.gps = gps.GPS()
        self.bno055 = bno055.BNO055()
        self.radio = radio.radio()
        self.RED_LED = led.led(ct.const.RED_LED_PIN)
        self.BLUE_LED = led.led(ct.const.BLUE_LED_PIN)
        self.GREEN_LED = led.led(ct.const.GREEN_LED_PIN)
        
        #開始時間の記録
        self.startTime = time.time()
        self.timer = 0
        self.landstate = 0 #landing stateの中でモータを一定時間回すためにlandのなかでもステート管理するため
        self.startstate = 0
        self.v_right = 100
        self.v_left = 100
        
        #変数
        self.state = 5
        self.laststate = 0
        self.landstate = 0
        self.k = 20
        self.v_ref = 90
        
        #スタート地点移動用の緯度経度
        #cansatGPS
        self.startlon=139.65603167
        self.startlat=35.55505667
        
        #google map
        #self.startlon=139.6559749
        #self.startlat=35.5549795
        
        self.realshadow=[[0,0],#永久影の設定15×15
                         [0,ct.const.SHADOW_EDGE_LENGTH],
                         [ct.const.SHADOW_EDGE_LENGTH,ct.const.SHADOW_EDGE_LENGTH],
                         [ct.const.SHADOW_EDGE_LENGTH,0]]
        self.shadow=[[-ct.const.MAX_SHADOW_EDGE_LENGTH,-ct.const.MAX_SHADOW_EDGE_LENGTH],#拡張永久影の設定25×25
                     [-ct.const.MAX_SHADOW_EDGE_LENGTH,ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH],
                     [ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH,ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH],
                     [ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH,-ct.const.MAX_SHADOW_EDGE_LENGTH]]
        self.startpoint=[[-ct.const.MAX_SHADOW_EDGE_LENGTH,ct.const.SHADOW_EDGE_LENGTH/2],#スタート地点の設定
                         [ct.const.SHADOW_EDGE_LENGTH/2,ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH],
                         [ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH,2/ct.const.SHADOW_EDGE_LENGTH],
                         [ct.const.SHADOW_EDGE_LENGTH/2,-ct.const.MAX_SHADOW_EDGE_LENGTH]]
        self.startshadowTHRE=[[-10,-5],#スタート地点の許容範囲[-10<x<-5 20<y<25 20<x<25 -10<y<-5]
                              [ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH,25],
                              [ct.const.SHADOW_EDGE_LENGTH + ct.const.MAX_SHADOW_EDGE_LENGTH,25],
                              [-10,-5]]
        self.close_startpoint=-1
        self.starttheta=0
        self.startpointdis=list()
        self.anglestate=0
        
        #オドメトリ用の変数
        self.x=0
        self.y=0
        self.q=0
        self.t1=0
        self.t2=0
        self.azimuth=[90, 0, 270, 180]
     
        #n点測位用の変数
        self.measureringTimeLog=list()
        self.measuringcount=0#n点測量目をこの変数で管理
        self.meanCansatRSSI=0
        self.meanLostRSSI=0
        self.LogData = list()
        self.n_LogData = list()
        self.LogCansatRSSI=list()
        self.LogLostRSSI=list()
        self.n_dis_LogCansatRSSI=list()
        self.n_dis_LogLostRSSI=list()
        self.n_meandisLog=list()
        self.n_LogCansatRSSI=list()
        self.n_LogLostRSSI=list()
        
        #探査機推定時用の変数
        self.X, self.Y = np.meshgrid(np.arange(-30, 31, 1), np.arange(-30, 31, 1))
        self.n_pdf=list()
        self.positioning_count=0
     
        #stateに入っている時刻の初期化
        self.preparingTime = 0
        self.flyingTime = 0
        self.droppingTime = 0
        self.landingTime = 0
        self.pre_motorTime = 0
        self.startingTime = 0
        self.measureringTime = 0
        self.runningTime = 0
        self.positioningTime = 0
        self.finishTime = 0
        
        #state管理用変数初期化
        self.countPreLoop = 0
        self.countFlyLoop = 0
        self.countDropLoop = 0
        self.countSwitchLoop=0
        self.countGoal = 0
        self.countgrass=0
        
        #GPIO設定
        GPIO.setmode(GPIO.BCM) #GPIOの設定
        GPIO.setup(ct.const.FLIGHTPIN_PIN,GPIO.IN) #フライトピン用
        
        date = datetime.datetime.now()
        self.filename = '{0:%Y%m%d}'.format(date)
        self.filename_hm = '{0:%Y%m%d%H%M}'.format(date)
        
        #csv
        self.cansatrssi=list()
        self.lostrssi=list()
        
        if not os.path.isdir('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s' % (self.filename)):
            os.mkdir('/home/pi/Desktop/wolvez2021/Testcode/Integration/%s' % (self.filename))
            
  
    
    def setup(self):
        self.gps.setupGps()
        self.radio.setupRadio()
        self.bno055.setupBno()

        if self.bno055.begin() is not True:
            print("Error initializing device")
            exit()
   
    def sensor(self):
        self.timer = 1000*(time.time() - self.startTime) #経過時間 (ms)
        self.timer = int(self.timer)
        self.gps.gpsread()
        self.bno055.bnoread()
        self.writeData()#txtファイルへのログの保存
    
        if not self.state == 1: #preparingのときは電波を発しない
            if not self.state ==5:#self.sendRadio()#LoRaでログを送信
                self.sendRadio()
            else:
                self.switchRadio()
            
    def odometry(self):
        self.t1=time.time()
        self.encoder.est_v_w(ct.const.RIGHT_MOTOR_ENCODER_A_PIN,ct.const.LEFT_MOTOR_ENCODER_A_PIN)#return self.encoder.cansat_speed, self.encoder.cansat_rad_speed
        self.t2=time.time()
        self.x,self.y,self.q=self.encoder.odometri(self.encoder.cansat_speed,self.encoder.cansat_rad_speed,self.t2-self.t1,self.x,self.y,self.q)

    def integ(self):#センサ統合用
        self.rightmotor.go(60)
        self.leftmotor.go(60)
              
    def keyboardinterrupt(self):
        self.RED_LED.led_on()
        self.BLUE_LED.led_off()
        self.GREEN_LED.led_off()
        self.rightmotor.stop()
        self.leftmotor.stop()

    def writeData(self):
        self.Ax=round(self.bno055.Ax,3)
        self.Ay=round(self.bno055.Ay,3)
        self.Az=round(self.bno055.Az,3)
        self.ex=round(self.bno055.ex,3)
        self.ey=round(self.bno055.ey,3)
        self.ez=round(self.bno055.ez,3)
        
        #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる
        datalog = str(self.timer) + ","\
                  + str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat).rjust(6) + ","\
                  + str(self.gps.Lon).rjust(6) + ","\
                  + str(self.Ax).rjust(6) + ","\
                  + str(self.Ay).rjust(6) + ","\
                  + str(self.Az).rjust(6) + ","\
                  + str(self.ex).rjust(6) + ","\
                  + str(self.rightmotor.velocity).rjust(6) + ","\
                  + str(self.leftmotor.velocity).rjust(6) + ","\
                  + str(self.encoder.cansat_speed).rjust(6) + ","\
                  + str(self.encoder.cansat_rad_speed).rjust(6) + ","\
                  + str(self.x).rjust(6) + ","\
                  + str(self.y).rjust(6) + ","\
                  + str(self.q).rjust(6) 
        print(datalog)
        '''
        if self.countSwitchLoop > ct.const.SWITCH_LOOP_THRE-1:
            datalog = str(self.radio.cansat_rssi) + ","\
                      + str(self.radio.lost_rssi) + ","\
                      + str(np.mean(self.LogCansatRSSI)) + ","\
                      + str(np.mean(self.LogLostRSSI)) + ","\
                      + str(np.std(self.LogCansatRSSI)) + ","\
                      + str(np.std(self.LogLostRSSI))+","\
                      + "finish"
            print(self.meanCansatRSSI)
        '''
        '''
        self.cansatrssi.append(str(self.radio.cansat_rssi))
        self.lostrssi.append(str(self.radio.lost_rssi))
        
        if self.countSwitchLoop > ct.const.SWITCH_LOOP_THRE-1:
            
            self.cansatrssi.append(str(self.radio.cansat_rssi))
            self.lostrssi.append(str(self.radio.lost_rssi))
            
                       
            self.cansatrssi.insert(0,str(np.mean(self.LogCansatRSSI)))
            self.lostrssi.insert(0, str(np.mean(self.LogLostRSSI)))
            
            self.cansatrssi.insert(1,str(np.std(self.LogCansatRSSI)))
            self.lostrssi.insert(1,str(np.std(self.LogLostRSSI)))
            
            
            
            position = input("position(m):")
            self.cansatrssi.insert(0, position + "m")
            self.lostrssi.insert(0, position + "m")
            self.cansatrssi.insert(0, "cansat")
            self.lostrssi.insert(0, "lost")    
            
            
            with open("%s/%s.csv" % (self.filename,self.filename_hm), "a", encoding='utf-8') as f: # 文字コードをShift_JISに指定 'a':末尾に追加
                writer = csv.writer(f, lineterminator='\n') # writerオブジェクトの作成 改行記号で行を区切る
                writer.writerow(self.cansatrssi) # csvファイルに書き込み
                writer.writerow(self.lostrssi)  
            
            self.cansatrssi=list()
            self.lostrssi=list()
#         ------------------------------------------------------------------------------------------
    '''
    
    def sendRadio(self):
        datalog = str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon) + ","\
                  #+ str(self.rightmotor.velocity) + ","\
                  #+ str(self.leftmotor.velocity)
        self.radio.sendData(datalog) #データを送信
        
    def switchRadio(self):
        datalog = str(self.state) + ","\
                  + str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon) + ","\
                  #+ str(self.rightmotor.velocity) + ","\
                  #+ str(self.leftmotor.velocity)
        self.radio.switchData(datalog) #データを送信    
    
    def sequence(self):
        if self.state == 0:
            self.preparing()
        elif self.state == 1:
            self.flying()
        elif self.state == 2:
            self.dropping()
        elif self.state == 3:
            self.landing()
        elif self.state == 4:
            self.starting()
        elif self.state == 5:
            self.measuring()
        elif self.state == 6:
            self.running()
        elif self.state == 7:
            self.positioning()
        elif self.state == 8:
            self.finish()
        else:
            self.state = self.laststate #どこにも引っかからない場合何かがおかしいのでlaststateに戻してあげる
    
    def preparing(self):#時間が立ったら移行
        if self.preparingTime == 0:
            self.preparingTime = time.time()#時刻を取得
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
        #self.countPreLoop+ = 1
        if not self.preparingTime == 0:
            if time.time() - self.preparingTime > ct.const.PREPARING_TIME_THRE:
                self.state = 1
                self.laststate = 1
    
    def flying(self):#フライトピンが外れたのを検知して次の状態へ以降
        if self.flyingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.flyingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
                
        if GPIO.input(ct.const.FLIGHTPIN_PIN) == GPIO.HIGH:#highかどうか＝フライトピンが外れているかチェック
            self.countFlyLoop+=1
            if self.countFlyLoop > ct.const.COUNT_FLIGHTPIN_THRE:#一定時間HIGHだったらステート移行
                self.state = 2
                self.laststate = 2
               
        else:
            self.countFlyLoop = 0 #何故かLOWだったときカウントをリセット
    
            
    def dropping(self):
        if self.droppingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.droppingTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_off()         
      
        #加速度が小さくなったら着地判定
        if (pow(self.bno055.Ax,2) + pow(self.bno055.Ay,2) + pow(self.bno055.Az,2)) < pow(ct.const.ACC_THRE,2):#加速度が閾値以下で着地判定
            self.countDropLoop+=1
            if self.countDropLoop > ct.const.COUNT_ACC_LOOP_THRE:
                self.state = 3
                self.laststate = 3
        else:
            self.countDropLoop = 0 #初期化の必要あり
        
    def landing(self):
        if self.landingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.landingTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
        
        if not self.landingTime == 0:
            if self.landstate == 0:
                self.servomotor.servo_angle(90)#サーボモータ動かしてパラ分離
                self.servomotor.stop()
                if time.time()-self.landingTime > ct.const.RELEASING_TIME_THRE:
                    #self.servomotor.servo_angle(0)
                    self.pre_motorTime = time.time()
                    self.landstate = 1
            #一定時間モータを回してパラシュートから離れる
            elif self.landstate == 1:
                self.rightmotor.go(100)
                self.leftmotor.go(100)

                if time.time()-self.pre_motorTime > ct.const.PRE_MOTOR_TIME_THRE:
                    self.rightmotor.stop()
                    self.leftmotor.stop()
                    self.state = 4
                    self.laststate = 4
                else:
                    pass
    
    def starting(self):
        if self.startingTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.startingTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_on()
            self.startpointdis=list()
        else:#4つのスタート地点から一番近い点へ移動
            #原点と着陸地点の距離と方位角を取得
            if self.startstate==0:
                self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)#距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
                #self.gps.vincenty_inverse(self.startlat,self.startlon,35.55518333,139.65596167)
                #極座標から直交座標へ変換
                self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))
                self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
                
                self.startpointdis.append(math.sqrt((self.x - self.startpoint[i][0])**2 + (self.y - self.startpoint[i][1])**2))

                for i in range(4):
                    startpointdis.append(math.sqrt((self.x - self.startpoint[i][0])**2 + (self.y - self.startpoint[i][1])**2))
                
                self.close_startpoint=self.startpointdis.index(min(self.startpointdis))#0~3の中で一番近いスタート地点のインデックスを格納
                self.starttheta=math.degrees(math.atan2(self.startpoint[self.close_startpoint][1] - self.y,self.startpoint[self.close_startpoint][0] - self.x))#スタート地点までの角度を計算
                self.startstate=1
            else:
                print("startpoint is "+ str(self.close_startpoint))
                if math.fabs(self.ex - self.starttheta) > ct.const.ANGLE_THRE:#一番近いスタート地点に向けて姿勢を変更
                    print(self.gps.gpsdegrees)
                    print("(x,y)"+str(self.x)+","+str(self.y))
#                     print("angle:"+str(self.starttheta))
#                     print("angle error:"+ str(math.fabs(self.ex - self.starttheta)))
                    self.rightmotor.back(30)
                    self.leftmotor.go(30)
                   
                else:#姿勢が変えらたら直進

                    self.rightmotor.go(self.v_ref)
                    self.leftmotor.go(self.v_ref)
                    self.odometry()
                
                    #選択したスタート地点に向かって直進し，大体近づいたら次のステートへ
                    if self.close_startpoint==0 or self.close_startpoint==2:
                        if  self.startshadowTHRE[self.close_startpoint][0] < self.x  and self.x < self.startshadowTHRE[self.close_startpoint][1]:
                            self.rightmotor.stop()
                            self.lefttmotor.stop()
                            self.state = 5
                            self.laststate = 5
                    
                    elif self.close_startpoint==1 or self.close_startpoint==3:
                        if  self.startshadowTHRE[self.close_startpoint][0] < self.y  and self.y < self.startshadowTHRE[self.close_startpoint][1]:
                            self.rightmotor.stop()
                            self.lefttmotor.stop()
                            self.state = 5
                            self.laststate = 5
                            
                if time.time() - self.startingTime > 30:#30秒経ってもスタート地点に着いてない場合は最初からやりなおす
                    self.startstate=0
                
                
            
    def measuring(self):
        print("measuring count is "+str(self.measuringcount))
        if self.measureringTimeLog == list():#時刻を取得してLEDをステートに合わせて光らせる
            self.measureringTimeLog.append(time.time())
            self.RED_LED.led_off()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
            self.rightmotor.stop()
            self.leftmotor.stop()
            
            if self.measuringcount == 0:#1回目測量時にGPSからself.xとself.yを算出
                self.gps.vincenty_inverse(self.startlat,self.startlon,self.gps.Lat,self.gps.Lon)#距離:self.gps.gpsdis 方位角:self.gps.gpsdegrees
                #極座標から直交座標へ変換
                self.x = self.gps.gpsdis*math.cos(math.radians(self.gps.gpsdegrees))
                self.y = self.gps.gpsdis*math.sin(math.radians(self.gps.gpsdegrees))
                
        else:
            if self.countSwitchLoop < ct.const.SWITCH_LOOP_THRE:
                #self.switchRadio()#LoRaでログを送信
                self.LogCansatRSSI.append([self.radio.cansat_rssi])
                self.LogLostRSSI.append([self.radio.lost_rssi])
                #print(self.countSwitchLoop)
                self.countSwitchLoop+=1
            else:
                #RSSIの平均取る
                self.meanCansatRSSI=np.mean(self.LogCansatRSSI)
                self.meanLostRSSI=np.mean(self.LogLostRSSI)
               
                #距離推定
                self.distanceCansatRSSI=self.radio.estimate_distance_Cansat(self.meanCansatRSSI)
                self.distanceLostRSSI=self.radio.estimate_distance_Lost(self.meanLostRSSI)
                print('カンサット:定義式からの推定'+str(self.distanceCansatRSSI))
                print('ロスト機:定義式からの推定'+str(self.distanceLostRSSI))
                self.n_dis_LogCansatRSSI.append(self.distanceCansatRSSI)
                self.n_dis_LogLostRSSI.append(self.distanceLostRSSI)
                self.meandis=(self.distanceCansatRSSI+self.distanceLostRSSI)/2
                self.n_meandisLog.append(self.meandis)                
                
                #n点測量後に使用するデータを格納
                self.LogData = [self.measuringcount,self.x,self.y,self.meandis,np.std(self.LogCansatRSSI),np.std(self.LogLostRSSI)]
                self.n_LogData.append(self.LogData)
                #RSSIのデータ保管
                self.n_LogCansatRSSI.append(self.LogCansatRSSI)
                self.n_LogCansatRSSI.append(self.LogLostRSSI)
                
                self.meanCansatRSSI=0
                self.meanLostRSSI=0
                self.mesureringTime = 0
                self.countSwitchLoop = 0
                self.LogCansatRSSI=[]
                self.LogLostRSSI=[]
                self.LogData=[]
                
                if self.measuringcount == ct.const.MAX_MEASURING_COUNT:
                    self.state = 7
                    self.laststate = 7
                
                else:
                    self.measuringcount+=1#n点測量目
                    self.state = 6
                    self.laststate = 6
            
    def caseDiscrimination(self):
        if self.x < 0 and self.y < ct.const.SHADOW_EDGE_LENGTH:
            self.case=0
        elif self.x < ct.const.SHADOW_EDGE_LENGTH and self.y > ct.const.SHADOW_EDGE_LENGTH:
            self.case=1
        elif self.x > ct.const.SHADOW_EDGE_LENGTH and self.y > 0:
            self.case=2
        elif self.x > 0 and self.y < 0:
            self.case=3
        else:#永久影に入っちゃっている場合
            self.case=4
    
    def motor_run(self):
        if self.case==1:        
            error=math.sin(math.radians(self.azimuth[self.case])) - math.sin(math.radians(self.bno055.ex))
            ke=self.k*error

            self.leftmotor.go(self.v_ref+ke)
            self.rightmotor.go(self.v_ref)

        elif self.case==2:
            error=math.cos(math.radians(self.azimuth[self.case])) - math.cos(math.radians(self.bno055.ex))
            ke=self.k*error
            self.leftmotor.go(self.v_ref+ke)
            self.rightmotor.go(self.v_ref)
        
        elif self.case==3:
            error=math.sin(math.radians(self.azimuth[self.case])) - math.sin(math.radians(self.bno055.ex))
            ke=self.k*error
            self.leftmotor.go(self.v_ref)
            self.rightmotor.go(self.v_ref+ke)
         
        elif self.case==0:
            error=math.cos(math.radians(self.azimuth[self.case])) - math.cos(math.radians(self.bno055.ex))
            ke=self.k*error
            self.leftmotor.go(self.v_ref)
            self.rightmotor.go(self.v_ref+ke)
    
    def running(self):
        if self.runningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            
            self.runningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_on()
            self.GREEN_LED.led_on()
        
        else:#Case判定  
            self.caseDiscrimination()#Case判定
            print("case is "+str(self.case))
            print("(x,y)"+str(self.x)+","+str(self.y))
            
            if self.case == 4:#永久影からの脱出
                
                self.rightmotor.go(60)
                self.leftmotor.go(80)
                self.odometry()
            else:

                if math.sqrt((self.x - self.n_LogData[self.measuringcount-1][1])**2 + (self.y - self.n_LogData[self.measuringcount-1][2])**2) > ct.const.MEASURMENT_INTERVAL:#前回の測量地点から閾値以上動いたらmeasurring stateへ
                        self.rightmotor.stop()
                        self.leftmotor.stop()
                        self.state = 5
                        self.laststate = 5
                else:
                    self.motor_run()
                    self.odometry()
                        
    def positioning(self):
        if self.positioningTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.positioningTime = time.time()
            self.RED_LED.led_on()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
            self.rightmotor.stop()
            self.leftmotor.stop()
        else:
            if self.positioning_count == self.measuringcount:
                self.n_pdf_sum=sum(self.n_pdf)
                self.graph(self.n_pdf_sum)
                self.state = 8
                self.laststate = 8
            else:
                self.n_pdf.append(self.pdf(self.n_LogData[self.positioning_count][1],
                                      self.n_LogData[self.positioning_count][2],
                                      self.n_LogData[self.positioning_count][3]))
                self.positioning_count +=1
        
    def finish(self):
        if self.finishTime == 0:#時刻を取得してLEDをステートに合わせて光らせる
            self.finishTime = time.time()
            self.RED_LED.led_off()
            self.BLUE_LED.led_off()
            self.GREEN_LED.led_off()
        
    def pdf(self,xc,yc,r):
        w=3
        return 0.5*np.exp(-((w*self.X-xc)**2+(w*self.Y-yc)**2)/(2*r**2))*((w*self.X-xc)**2+(w*self.Y-yc)**2)/(2*math.pi*r**2)       
             
    def graph(self,Z):
        Zc=np.unravel_index(np.argmax(Z), Z.shape)
        print("Zc:" + str(Zc))
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        surf=ax.plot_surface(self.X, self.Y, Z, cmap=plt.cm.jet,linewidth=0, antialiased=False)
        ax.scatter(x[Zc[1]], y[Zc[0]], np.max(Z),s = 40,c='k',)
        ax.set_xlim(-30.01, 30.01)
        ax.set_ylim(-30.01, 30.01)
        ax.set_zlim(0.0, 0.5)
        ax.view_init(30, 30)
        fig.colorbar(surf, shrink=0.5, aspect=5)
        plt.show()

if __name__ == "__main__":
    pass

