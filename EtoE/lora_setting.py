# -*- coding: utf-8 -*-
import serial
import time
import RPi.GPIO as GPIO


# LoRa設定用クラス
class LoraSettingClass:

    def __init__(self, serial_device=''):
        try:  # インスタンス変数 serialDevice を生成
            self.device = serial.Serial(serial_device, 9600)
        except Exception as e:
            error_mes = '{0}'.format(e)
            print(error_mes)
        self.cmd = None
        self.reset_pin = 18

    # LoRaに対して命令コマンドを入力する
    def cmd_lora(self, cmd=''):
        if not cmd:  # cmdが未入力の場合は終了
            print('cmdが入力されていません')
            return
        self.cmd = '{0}\r\n'.format(cmd)
        self.device.write(self.cmd.encode())

    # LoRaリセット
    def reset_lora(self):
        pass
#         GPIO.setmode(GPIO.BOARD)
#         GPIO.setup(self.reset_pin, GPIO.OUT)
#         GPIO.output(self.reset_pin, GPIO.HIGH)
#         time.sleep(0.1)
#         GPIO.output(self.reset_pin, GPIO.LOW)
#         time.sleep(0.1)
#         GPIO.cleanup()
#         time.sleep(0.1)

    def setup_lora(self):
        # LoRa(ES920LR)設定
#         print("setting up lora")
        print("##### debug ROI start #####")
        set_mode=['1','d','15','e','0001','f','0002','g','0001','n','2','l','2','p','1','y','z']
        self.set_mode = set_mode
        print("##### debug ROI end #####")
        
        # LoRa(ES9320LR)起動待機
#         while self.device.inWaiting() > 0:
#             try:
#                 line = self.device.readline()
#                 if line.find(b'Select'):
#                     line = line.decode("utf-8")
#                     print(line)
#             except Exception as e:
#                 print(e)
#                 continue
        # LoRa(ES920LR)コマンド入力
        for cmd in self.set_mode:
            self.cmd_lora(cmd)
            time.sleep(0.1)
        print("set_mode end")
        time.sleep(1)
        print("sleep end")
        
        while self.device.inWaiting() > 0:
            print("##### enter while loop in lora_setting.py #####")
            try:
                line = self.device.readline()
                line = line.decode("utf-8")
                print(line)
            except Exception as e:
                print(e)
                continue

    def close(self):
        self.device.close()
