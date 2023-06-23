# -*- coding: utf-8 -*-
import time
import sys
import lora_send_onlyOnce
import RPi.GPIO as GPIO
import constant as ct

lora_device = "/dev/ttyAMA1"
channel = input('channel:')

# ピンの定義
## GPIO設定
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM) #GPIOの設定
# GPIO.setup(ct.const.FLIGHTPIN_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP) #フライトピン用。プルアップを有効化
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN)
# LoRaの設定


# 一定時間，送信
lr_send = lora_send_onlyOnce.LoraSendClass(lora_device, channel)
start=time.time()
while time.time()-start<3:
    lr_send.lora_send()
    print(f"message sent at {time.time()}")


# 停止
print("### state changed. Stop sending message ###")

# フライトピン抜くと起動
countFlyLoop=0
while True:
    if GPIO.input(ct.const.FLIGHTPIN_PIN) == GPIO.HIGH: #highかどうか＝フライトピンが外れているかチェック
        countFlyLoop+=1
        print("counting up for detection")
        if countFlyLoop > ct.const.FLYING_FLIGHTPIN_COUNT_THRE: #一定時間HIGHだったらステート移行
            break

while True:
    lr_send.lora_send()
