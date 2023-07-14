# -*- coding: utf-8 -*-

import cansat
import time
import RPi.GPIO as GPIO
import sys
import constant as ct


can=cansat.Cansat()
can.setup()
GPIO.setwarnings(False)

try:
    while True:
        #can.integ()
        can.sensor()
        time.sleep(0.05)
        can.sequence()

except KeyboardInterrupt:
    print('finished')
    can.keyboardinterrupt()
    GPIO.cleanup()
    can.rightmotor.stop()
    can.leftmotor.stop()
    pass
