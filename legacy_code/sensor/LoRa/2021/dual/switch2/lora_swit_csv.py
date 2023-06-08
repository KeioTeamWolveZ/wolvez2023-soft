# -*- coding: utf-8 -*-
from typing import Counter
import lora_setting
import time
import csv
import numpy as np


# LoRa送受信用クラス（受信したらRSSIを送り返す）
class LoraSwitClass:

    def __init__(self, lora_device, channel):
        self.switDevice = lora_setting.LoraSettingClass(lora_device)
        self.channel = channel

    # ES920LRデータ送受信メソッド
    def lora_swit(self):
        # LoRa初期化
        self.switDevice.reset_lora()
        # LoRa設定コマンド

        set_mode = ['1', 'd', self.channel, 'e', '0001', 'f', '0002', 'g', '0001',
                    'n', '2', 'l', '2', 'p', '1', 'y', 'z']
        # LoRa設定
        self.switDevice.setup_lora(set_mode)
        # LoRa(ES920LR)受信待機

        filename = input("filename:")

        while True:

            rssi_list = ["rssi"]
            data_list = ["data"]

            position = input("position(m):")
            rssi_list.append(position + "m")
            data_list.append(position + "m")

            count = 0
            while count < 30: # 50個データがたまるまでループ
                try:
                    print(count)
                    print(rssi_list)
                    print(data_list)
                    # 送るデータ
                    senddata = 'aaaa'
                    print('<-- SEND -- [{} ]'.format(senddata))
                    self.switDevice.cmd_lora('{}'.format(senddata))
                   #time_now = time.time()
                   # while True:
                   #     print(time.time()-time_now)
                   #     if time.time()-time_now>2:
                   #         print("timeout")
                   #         break
                    time.sleep(2.0)    #seconds              
                    
                    # ES920LRモジュールから値を取得   
                    while self.switDevice.device.inWaiting() > 3:
                            #print("recieved")
                            #print(time.time())
                        
                            line = self.switDevice.device.readline()
                            line = line.decode("utf-8")
                            #print("decode")
                            #print(time.time())
                            print(line)
                            
                        
                            #print(line)
                            if line.find('RSSI') >= 0 and line.find('information') == -1:
                                print("findRSSI")
                                
                                log = line
                                log_list = log.split('):Receive Data(')
                                # 受信電波強度

                                rssi = log_list[0][5:8]#0-4
                                print(rssi)#自分が受けたRSSI
                                # 受信フレーム
                                data = log_list[1][0:3]#1-最後から3番目の1個前まで
                                print('Receive'+ data)
                                print('-------------')     

                                count += 1
                                rssi_list.append(str(rssi))
                                data_list.append(str(data))

                                    
                
                    
                except KeyboardInterrupt:
                    self.switDevice.close()
                    
                #5
                # time.sleep(1)
            
            # rssi_mean = sum(list(map(int, rssi_list[2:])))/len(rssi_list[2:]) #平均値
            # rssi_vari = #標準偏差は今回は標本から平均を求めているから普遍分散？

            # data_mean = sum(list(map(int, data_list[2:])))/len(data_list[2:]) #平均値
            rssi_int = list(map(int, rssi_list[2:]))
            data_int = list(map(int, data_list[2:]))
            
            
            rssi_list.append(str(np.mean(rssi_int)))
            data_list.append(str(np.mean(data_int)))
            rssi_list.append(str(np.std(rssi_int)))
            data_list.append(str(np.std(data_int)))


            with open(str(filename)+".csv", "a", encoding='utf-8') as f: # 文字コードをShift_JISに指定 'a':末尾に追加
                writer = csv.writer(f, lineterminator='\n') # writerオブジェクトの作成 改行記号で行を区切る
                writer.writerow(rssi_list) # csvファイルに書き込み
                writer.writerow(data_list)  



