import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(25,GPIO.OUT) #焼き切り用のピンの設定

try:
    GPIO.output(25,1) #電圧をHIGHにして焼き切りを行う
    time.sleep(10) #継続時間を指定
    GPIO.output(25,0) #電圧をLOWにして焼き切りを終了する
    GPIO.cleanup()

except:
    GPIO.output(25,0) #電圧をLOWにして焼き切りを終了
    GPIO.cleanup()
