# -*- coding: utf-8 -*-
import time
import lora_setting


# LoRa送信用クラス
class LoraSendClass:

    def __init__(self, lora_device, channel):
        self.sendDevice = lora_setting.LoraSettingClass(lora_device)
        self.channel = channel
        self.sendDevice.reset_lora()
        # LoRa初期化
        self.sendDevice.reset_lora()
        # LoRa設定コマンド
        set_mode = ['1', 'd', self.channel, 'e', '0001', 'f', '0002', 'g', '0001', 
                    'n', '2', 'l', '2', 'p', '1', 'y', 'z']
#         # LoRa設定
        self.sendDevice.setup_lora(set_mode)

    # ES920LRデータ送信メソッド
    def lora_send(self,data=""):
        # LoRa初期化
        #self.sendDevice.reset_lora()
        # LoRa設定コマンド
        #set_mode = ['1', 'd', self.channel, 'e', '0001', 'f', '0002', 'g', '0001',
        #            'n', '2', 'l', '2', 'p', '1', 'y', 'z']
#         # LoRa設定
        #self.sendDevice.setup_lora(set_mode)
        # LoRa(ES920LR)データ送信
                # 送るデータ
        if data == "":
            data = f'00010002-{time.time():.1f}'
        print(f'<-- SEND -- [{data}]')
        self.sendDevice.cmd_lora(data)
            # 5秒待機
