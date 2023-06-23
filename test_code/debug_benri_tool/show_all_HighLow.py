# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import numpy as np

GPIO.setmode(GPIO.BCM)
valid_IO=[]

for i in np.arange(1,30):
    try:
        GPIO.setup(i,GPIO.IN)
        valid_IO.append(i)
    except:
        pass

print(f"valid IO no. --> {valid_IO}")

while True:
    HL_data=[]
    for i in valid_IO:
        HL_data.append(GPIO.input(i))
    print(f"PIN : {valid_IO}")
    print(f"H/L : {HL_data}")
    print("")
    time.sleep(0.5)