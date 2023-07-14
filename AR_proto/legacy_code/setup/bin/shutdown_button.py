import time
import RPi.GPIO as GPIO
import os

GPIO.setmode(GPIO.BCM)
GPIO.setup(22,GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        GPIO.wait_for_edge(22, GPIO.FALLING)
        sw_counter = 0

        while True:
            sw_status = GPIO.input(22)

            if sw_status == 0:
                sw_counter = sw_counter + 1
                if sw_counter >= 200: #2秒以上押し続けるとshutdownコマンド実行
                    os.system("sudo shutdown -h now")
                    break
            else:
                break
