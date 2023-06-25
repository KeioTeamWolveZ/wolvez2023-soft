import motor
import RPi.GPIO as GPIO
import time 
import numpy as np
from datetime import datetime
import constant as ct
import lora_send_onlyOnce

lora_device = "/dev/ttyAMA1"
channel = 15
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4,GPIO.IN)
lr_send = lora_send_onlyOnce.LoraSendClass(lora_device, channel)

Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)

for i in np.arange(0,30*60):
    lr_send.lora_send("wait for run")
    print(f"message sent at {time.time()}")
    time.sleep(1)


try:
    print("motor run")
    Motor1.go(70)
    Motor2.go(70)
    i=0
    while i < 60*120/5:
        i+=1
        print("current time: "+str(datetime.now()))
        lr_send.lora_send(f"run count:{5*i}s")
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
