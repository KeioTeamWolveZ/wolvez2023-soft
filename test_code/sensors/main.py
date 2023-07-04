# -*- coding: utf-8 -*-
import sys
import time
import cv2
import RPi.GPIO as GPIO

import motor
import gps
import micropyGPS
import bno055
import lora_send

from libcam_module import Picam


def lora_data(states=1,gps_data=[1,1]): #通信モジュールの送信を行う関数
    send_data = "Lat:" + str(gps_data[0]) + "," \
            "Lon:" + str(gps_data[1])
    return send_data

def logging(states):
    datalog = str(int(1000*(time.time() - startTime_time))) + ","\
                  + "state:"+str(state)+ ","\
                  + "Time:"+str(gps.Time) + ","\
                  + "Lat:"+str(gps.Lat).rjust(6) + ","\
                  + "Lng:"+str(gps.Lon).rjust(6) + ","\
                  + "ax:"+str(round(ax,6)).rjust(6) + ","\
                  + "ay:"+str(round(ay,6)).rjust(6) + ","\
                  + "az:"+str(round(az,6)).rjust(6) + ","\
                  + "q:" + str(ex).rjust(6) + ","\
                  + "rV:" + str(round(MotorR.velocity,2)).rjust(4) + ","\
                  + "lV:" + str(round(MotorL.velocity,2)).rjust(4)
    print(datalog)

if __name__ == '__main__':
    state = 1
    
    GPIO.setwarnings(False)
    MotorR = motor.motor(6,5,13)
    MotorL = motor.motor(20,16,12)
    MotorR.go(50)
    MotorL.go(50)
    
    lora_device = "/dev/ttyAMA1"  # ES920LRデバイス名 (UART2) 
    channel = 15
    lr_send = lora_send.LoraSendClass(lora_device, channel)
    bno = bno055.BNO055()
    bno.setupBno()
    gps = gps.GPS()
    pc2 = Picam()
    # gps_obj = micropyGPS.MicropyGPS(9,'dd') # MicroGPSオブジェクトを生成する。
                                        # 引数はタイムゾーンの時差と出力フォーマット
    gps.setupGps()
    
    startTime_time = time.time()
    while True:
        try:
            # 各データの取得
            bno.bnoread()
            ax=round(bno.ax,3)
            ay=round(bno.ay,3)
            az=round(bno.az,3)
            ex=round(bno.ex,3)
            bno_data = [ax,ay,az]
            gps_data = gps.gpsread()

            # カメラ撮影
            img = pc2.capture(1)
            pc2.show(img)
            
            # データを結合して送信
            logging(state)
            lr_data = lora_data(gps_data=gps_data)
            # all_data = lora_data(bno_data=bno_data,gps_data=gps_data)
            # all_data = lora_data()
            print(lr_data)
            lr_send.lora_send(lr_data)
            
            # 画像を表示している場合はescキーで終了できる
            key = cv2.waitKey(1)
            # If you push "esc-key", this roop is finished.
            if key == 27:
                MotorR.stop()
                MotorL.stop()
                GPIO.cleanup()
                pc2.stop()
                lr_send.sendDevice.close()
                sys.exit()
                # cv2.imwrite("test_cv2.jpg", im)
                break

            time.sleep(0.5)
            
        except KeyboardInterrupt:
            MotorR.stop()
            MotorL.stop()
            GPIO.cleanup()
            pc2.stop()
            lr_send.sendDevice.close()
            sys.exit()
