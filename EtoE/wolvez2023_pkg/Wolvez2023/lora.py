# -*- coding: utf-8 -*-
import time

class lora:
    
    def __init__(self):
        # ES920LRデバイス名
        # ラズパイ3で使うときはttySOFT0
        import LoraSettingClass
        self.lora_device = "/dev/ttyAMA1"      
        self.sendDevice = LoraSettingClass(self.lora_device)
                # LoRa初期化
#         self.sendDevice.reset_lora()
#         # LoRa設定コマンド
#         set_mode = ['1', 'd', '15', 'e', '0001', 'f', '0001', 'g', '0002',
#                     'l', '2', 'n', '2', 'p', '1', 'y', 'z']
#         # LoRa設定
#         self.sendDevice.setup_lora(set_mode)
        
    def sendData(self, datalog):
        self.sendDevice.cmd_lora("00010002{}".format(datalog))
#         print("send:{}".format(datalog))