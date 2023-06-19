import RPi.GPIO as GPIO
import time
import motor
from bno055 import BNO055

#pin1 = 25
#pin2 = 24
#pin3 = 8

pin1 = 25
flight_pin = 4

Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin1,GPIO.OUT) #焼き切り用のピンの設定
GPIO.output(pin1,0) #焼き切りが危ないのでlowにしておく

GPIO.setmode(GPIO.BCM) #GPIOの設定
bno055 = bno055.BNO055()
bno055.setupBno()

if bno055.begin() is not True:
    print("Error initializing device")
    exit()

bno055 = BNO055()
countFlyLoop = 0
try:
    while True:
        bno055.bnoread()
        if GPIO.input(flight_pin) == GPIO.HIGH: #highかどうか＝フライトピンが外れているかチェック
            countFlyLoop+=1
            if countFlyLoop > 1000000: #一定時間HIGHだったらステート移行
                state = 2
                laststate = 2
        elif (bno055.ax**2 + bno055.ay**2 + bno055.az**2) < 1**2: #加速度が閾値以下で着地判定
            countDropLoop+=1            
            if countDropLoop > 100: #着地判定が複数回行われたらステート以降
                state = 3
                laststate = 3
            GPIO.output(pin1,1) #電圧をHIGHにして焼き切りを行う
            time.sleep(10) #継続時間を指定
            GPIO.output(pin1,0) #電圧をLOWにして焼き切りを終了する
            GPIO.cleanup()

            Motor1.go(50)
            Motor2.go(50)
            time.sleep(5)
            Motor1.stop()
            Motor2.stop()

            GPIO.cleanup()
            break
        else:
            countDropLoop = 0 #初期化の必要あり

except:
    GPIO.output(pin1,0) #電圧をLOWにして焼き切りを終了
    GPIO.cleanup()