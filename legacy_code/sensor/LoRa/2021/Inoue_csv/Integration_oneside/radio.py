# -*- coding: utf-8 -*-

import time
import radio_setting
import re

# LoRa送信用クラス
class radio(object):
    
    def __init__(self):
        # ES920LRデバイス名
        # ラズパイ3で使うときはttySOFT0
        # ラズパイ4で使うときはttyAMA1
        self.lora_device = "/dev/ttyAMA1"
        self.cansat_rssi=0
        self.lost_rssi=0
        self.LogCansatRSSI=list()
        self.LogLostRSSI=list()
        """
        #config設定
        self.channel = 15   #d
        self.panid = '0001' #e
        self.ownid = '0001' #f
        self.dstid = '0000' #g
        """
        
        self.sendDevice = radio_setting.LoraSettingClass(self.lora_device)
        
    def setupRadio(self):
        """
        # LoRa初期化
        self.sendDevice.reset_lora()
        """
        """
        # LoRa設定コマンド
        set_mode = ['1', 'd', self.channel, 'e', self.panid, 'f', self.ownid, 'g', self.dstid,
                    'l', '2', 'n', '1', 'p', '1', 'y', 'z']
                    #l:Ack(ON), n:転送モード(Payload), p:受信電波強度, y:show, z:start
        #os.system("sudo insmod soft_uart.ko")#os
                
        # LoRa設定
        self.sendDevice.setup_lora(set_mode)
        """
        # LoRa設定
        self.sendDevice.setup_lora()
    
    # ES920LRデータ送信メソッド
    def sendData(self, datalog):        
        # LoRa(ES920LR)データ送信
        #print(datalog)
        self.sendDevice.cmd_lora(datalog)
    
    def switchData(self, datalog):

        self.sendDevice.cmd_lora(datalog)
        
        while True:
#         for len(self.LogCansatRSSI) in self.const.SWITCH_LOOP_THRE
#             self.sendDevice.cmd_lora(datalog)
        
            if self.sendDevice.device.inWaiting() > 0:
                start=time.time()

                line = self.sendDevice.device.readline()
                line = line.decode("utf-8")

                
                if line.find('RSSI') >= 0 and line.find('information') == -1:        
                    time1=time.time()-start
                    time1_=time.time()
                    print("time1:"+str(time1))
                    
                    
                    log = line
                    ##log_list = log.split('):Receive Data(')
                    log_list = log.split('dBm):PAN ID(0001):Src ID(0001):Receive Data(')
                    time2=time.time()-time1_
                    time2_=time.time()
                    print("time2:"+str(time2))
                    
                    self.LogCansatRSSI.append(float(log_list[0][5:]))
                    self.LogLostRSSI.append(float(log_list[1][0:-3]))             
                  
                    
                    time3=time.time()-time2_
                    time3_=time.time()
                    print("time3:"+str(time3))
                                      
                    print('-------------')
                    break

    def estimate_distance_Cansat(self,meanCansatRSSI):
        #定義式より推定 
        N_Cansat=2.933
        MP_Cansat=-37.43
       
        return 10**((MP_Cansat-meanCansatRSSI)/(10*N_Cansat))       
    
    def estimate_distance_Lost(self,meanLostRSSI):
        #定義式より推定
        N_Lost=2.933
        MP_Lost=-37.30

        return 10**((MP_Lost-meanLostRSSI)/(10*N_Lost))
        
  


        
        
