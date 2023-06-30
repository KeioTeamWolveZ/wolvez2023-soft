import RPi.GPIO as GPIO
import time

#pin1 = 25
#pin2 = 24
#pin3 = 8

pin1 = 8

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin1,GPIO.OUT) #焼き切り用のピンの設定
GPIO.output(pin1,0) #焼き切りが危ないのでlowにしておく

try:
    GPIO.output(pin1,1) #電圧をHIGHにして焼き切りを行う
    time.sleep(10) #継続時間を指定
    GPIO.output(pin1,0) #電圧をLOWにして焼き切りを終了する
    GPIO.cleanup()

except:
    GPIO.output(pin1,0) #電圧をLOWにして焼き切りを終了
    GPIO.cleanup()
