# -*- coding: utf-8 -*-
import lora_setting
import time

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
        while True:
            try:
                # 送るデータ
                senddata = 'aaaa'
                
                self.switDevice.cmd_lora('{}'.format(senddata))
                print('<-- SEND -- [{} ]'.format(senddata))
               # time.sleep(0.5)                  
                
                # ES920LRモジュールから値を取得              
                while True:
                    if self.switDevice.device.inWaiting() > 0:
                    
                        line = self.switDevice.device.readline()
                        line = line.decode("utf-8")
                    
                        #print(line)
                        if line.find('RSSI') >= 0 and line.find('information') == -1:
                            
                            log = line
                            log_list = log.split('):Receive Data(')
                            # 受信電波強度

                            rssi = log_list[0][5:11]#0-4
                            print(rssi)#自分が受けたRSSI
                            # 受信フレーム
                            data = log_list[1][0:6]#1-最後から3番目の1個前まで
                            print('Receive'+ data)
                            print('-------------')
                            break  
#                         except Exception as e:
#                             print(e)
#            
                
            except KeyboardInterrupt:
                self.switDevice.close()
                
            #5
            time.sleep(1)


