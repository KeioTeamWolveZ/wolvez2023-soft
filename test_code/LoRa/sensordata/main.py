# -*- coding: utf-8 -*-
import sys
import time

import gps
import micropyGPS
import bno055
import lora_send


def combine_data(states=1,bno_data=1,gps_data=1): #通信モジュールの送信を行う関数
    datalog = "Test-state" + str(states) + ","\
        + "GPS DATA" + str(bno_data[0]) + ","
    return datalog

if __name__ == '__main__':
    lora_device = "/dev/ttyAMA1"  # ES920LRデバイス名 (UART2) 
    channel = 15
    lr_send = lora_send.LoraSendClass(lora_device, channel)
    bno = bno055.bno()
    gps_obj = micropyGPS.MicropyGPS(9,'dd') # MicroGPSオブジェクトを生成する。
                                        # 引数はタイムゾーンの時差と出力フォーマット
    #gps.thread(gps_obj)
    
    while True:
        try:
            # 各データの取得
            bno_data = bno.get_data()
            #gps_data = gps.gpsread(gps_obj)
            
            # データを結合して送信
            all_data = combine_data(bno_data=bno_data)
            #all_data = combine_data(bno_data=bno_data,gps_data=gps_data)
            #all_data = combine_data()
            print(all_data)
            lr_send.lora_send(all_data)
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            lr_send.sendDevice.close()
            sys.exit()
