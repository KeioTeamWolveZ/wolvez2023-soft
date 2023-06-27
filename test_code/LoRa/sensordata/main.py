# -*- coding: utf-8 -*-
import sys
import time

import gps
import micropyGPS
import bno055
import lora_send

from libcam_module import Picam


def combine_data(states=1,bno_data=1,gps_data=[1,1]): #通信モジュールの送信を行う関数
    datalog = "ax:" + str(bno_data[0]) + "," \
            "ay:" + str(bno_data[1]) + "," \
            "az:" + str(bno_data[2]) + "," \
            "LAT:" + str(gps_data[0]) + "," \
            "LON:" + str(gps_data[1])
    return datalog

if __name__ == '__main__':
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
            all_data = combine_data(bno_data=bno_data)
            # all_data = combine_data(bno_data=bno_data,gps_data=gps_data)
            # all_data = combine_data()
            print(all_data)
            lr_send.lora_send(all_data)
            
            # 画像を表示している場合はescキーで終了できる
            key = cv2.waitKey(1)
            # If you push "esc-key", this roop is finished.
            if key == 27:
                pc2.stop()
                lr_send.sendDevice.close()
                sys.exit()
                # cv2.imwrite("test_cv2.jpg", im)
                break

            time.sleep(2)
            
        except KeyboardInterrupt:
            pc2.stop()
            lr_send.sendDevice.close()
            sys.exit()
