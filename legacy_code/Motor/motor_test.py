import motor
import RPi.GPIO as GPIO
import time 


GPIO.setwarnings(False)
Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

try:
    print("motor run") 
#     Motor1.go(100)
#     Motor2.go(100)
#     Motor1.back(80)
#     Motor2.go(80)
#     time.sleep(0.5)
    #Motor1.go(70)
    Motor2.back(70)
#     time.sleep(1.08)
    time.sleep(0.02)

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

