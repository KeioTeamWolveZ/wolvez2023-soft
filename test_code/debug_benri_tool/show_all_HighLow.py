# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
from datetime import datetime
import numpy as np

GPIO.setmode(GPIO.BCM)
valid_IO=[]

for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]: 
    print(i) 
#    try:
    GPIO.setup(i,GPIO.IN)
    valid_IO.append(str(i).zfill(2))
#    except:
        #pass

print(f"valid IO no. --> {valid_IO}")

while True:
    HL_data=[]
    for i in valid_IO:
        data=str(GPIO.input(int(i)))
        HL_data.append(data.zfill(2))
    print(f"{datetime.now()} | PIN : {valid_IO}")
    print(f"{datetime.now()} | H/L : {HL_data}")
    print("")
    time.sleep(0.5)
