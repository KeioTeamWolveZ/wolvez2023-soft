import RPi.GPIO as GPIO
import time

pin1 = 8
pin2 = 25
pin3 = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin3,GPIO.OUT) #焼き切り用のピンの設定

try:
    GPIO.output(pin3,1) #電圧をHIGHにして焼き切りを行う
    time.sleep(10) #継続時間を指定
    GPIO.output(pin3,0) #電圧をLOWにして焼き切りを終了する
    GPIO.cleanup()

except:
    GPIO.output(pin3,0) #電圧をLOWにして焼き切りを終了
    GPIO.cleanup()
