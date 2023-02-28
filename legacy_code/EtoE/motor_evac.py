import motor2
import RPi.GPIO as GPIO
import time 

GPIO.setwarnings(False)
Motor1 = motor2.motor(5,6,13)
#Motor2 = motor.motor(20,21,12)

try:
    print("motor run") 
    Motor1.go(90)
    #Motor2.go(100)
    time.sleep(1)

    #Motor.back(100)
    #time.sleep(3)
    print("motor stop")
    Motor1.stop()
    #Motor2.stop()
    time.sleep(1)
except KeyboardInterrupt:
    Motor1.stop()
    #Motor2.stop()
    GPIO.cleanup()

GPIO.cleanup()

