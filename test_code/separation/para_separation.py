import RPi.GPIO as GPIO
import time
import motor

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

countFlyLoop = 0
try:
    while True:
        if GPIO.input(flight_pin) == GPIO.HIGH: #highかどうか＝フライトピンが外れているかチェック
            countFlyLoop+=1
            if countFlyLoop > 1000000: #一定時間HIGHだったらステート移行
                state = 2
                laststate = 2
        else:
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

except:
    GPIO.output(pin1,0) #電圧をLOWにして焼き切りを終了
    GPIO.cleanup()