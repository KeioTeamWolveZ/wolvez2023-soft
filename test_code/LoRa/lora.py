# -*- coding: utf-8 -*-
import time
import lora_setting

class lora:
    
    def __init__(self):
        # ES920LRデバイス名
        # ラズパイ3で使うときはttySOFT0
        self.lora_device = "/dev/ttyAMA1"      
        self.sendDevice = lora_setting.LoraSettingClass(self.lora_device)
        # LoRa初期化
        self.sendDevice.reset_lora()
        # LoRa設定コマンド
        set_mode = ['1', 'd', '15', 'e', '0001', 'f', '0002', 'g', '0001',
                    'n', '2', 'l', '2', 'p', '1', 'y', 'z']
        # LoRa設定
        # self.sendDevice.setup_lora()
        
    def sendData(self, datalog):
        print(datalog)
        self.sendDevice.cmd_lora("00010002{}".format(datalog))
#         print("send:{}".format(datalog))
