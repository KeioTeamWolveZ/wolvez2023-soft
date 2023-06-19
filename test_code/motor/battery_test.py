import motor
import RPi.GPIO as GPIO
import time 
from datetime import datetime

GPIO.setwarnings(False)
Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

time.sleep(30*60)

try:
    print("motor run") 
#     Motor1.go(100)
#     Motor2.go(100)
#     Motor1.back(80)
#     Motor2.go(80)
#     time.sleep(0.5)
    Motor1.go(70)
    Motor2.go(70)
    #Motor2.back(90)
    #time.sleep(1.08)
    i=0
    while i < 60*120/5:
        i+=1
        print("current time: "+str(datetime.now()))
        time.sleep(5)


    time.sleep(60*120)

    #Motor.back(100)
    #time.sleep(3)
    print("motor stop")
    Motor1.stop()
    Motor2.stop()
    time.sleep(1)
except KeyboardInterrupt:
    Motor1.stop()
    Motor2.stop()
    time.sleep(1)
    GPIO.cleanup()
    

GPIO.cleanup()
