import time
import RPi.GPIO as GPIO
 
class servomotor():
    def __init__(self,pin): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(pin, GPIO.OUT)
        self.pin = pin
        self.pwm = GPIO.PWM(self.pin,50) #電圧を参照するピンを周波数50HZに指定
        self.pwm.start(0.0)
        
    def servo_angle(self,angle):
        duty = 2.5 + (12.0 - 2.5) * (angle + 90) / 180   #角度からデューティ比を求める
        self.pwm.ChangeDutyCycle(duty)     #デューティ比を変更
        time.sleep(0.3)
        
    def stop(self):
        self.pwm.stop()
        self.pwm.ChangeDutyCycle(0.0)
