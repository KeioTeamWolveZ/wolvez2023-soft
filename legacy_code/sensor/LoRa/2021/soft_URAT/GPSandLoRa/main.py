#【mission_func/cansat.py】からgps・loraに関係ない部分をコメントアウト

"""
Keio Wolve'Z cansat2020
mission function
Author Yuji Tanaka
date:2020/05/26
"""
#ライブラリの読み込み
import time
import gps
import radio
import os
#import motor
#import RPi.GPIO as GPIO

class Cansat(object):
    
    def __init__(self):
        self.gps = gps.GPS()
        self.radio = radio.radio()
        
        #開始時間の記録
        self.startTime = time.time()
        self.timer = 0
    
    def setup(self): #self追加
        self.gps.setupGps()
        self.radio.setupRadio()
        
    def sensor(self):
        self.gps.gpsread()
        self.writeData()#txtファイルへのログの保存
        self.sendRadio()#LoRaでログを送信
    
    def writeData(self):
        self.timer = 1000*(time.time() - self.startTime) #経過時間 (ms)
        self.timer = int(self.timer)
        #ログデータ作成。\マークを入れることで改行してもコードを続けて書くことができる
        
        datalog = str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon)
                  
        
        with open("test.txt",mode = 'a') as test: # [mode] x:ファイルの新規作成、r:ファイルの読み込み、w:ファイルへの書き込み、a:ファイルへの追記
            test.write(datalog + '\n')
            
          
    def sendRadio(self):
        #datalog = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        
        datalog = str(self.gps.Time) + ","\
                  + str(self.gps.Lat) + ","\
                  + str(self.gps.Lon)
        print(datalog)
                  

        self.radio.sendData(datalog) #データを送信
            
if __name__ == "__main__":
    pass

#追記↓


#os.system("sudo insmod soft_uart.ko")
cansat = Cansat()
#Motor = motor.motor(5,6,13)
cansat.setup()
while True:
    try:
        cansat.sensor()
        """
        print("motor run")
        Motor.go(100)
        time.sleep(3)
        print("motor stop")
        Motor.stop()
        time.sleep(3)
        """
    except KeyboardInterrupt:
        #Motor.stop()
        self.sendDevice.close()
        #GPIO.cleanup()
    # 1秒待機
    #time.sleep(0.5)