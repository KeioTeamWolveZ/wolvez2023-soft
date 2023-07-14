import numpy as np
import cansat
import time
import RPi.GPIO as GPIO
import sys
import constant as ct

can=cansat.Cansat()
can.setup()
GPIO.setwarnings(False)
i=0
try:
    while i<5:
        while can.countSwitchLoop<10:
            can.LogCansatRSSI += [1]
            can.LogLostRSSI += [1]
            print('-----------------------')
            print(can.LogCansatRSSI)
            print(can.LogLostRSSI)
            can.countSwitchLoop+=1
            time.sleep(0.05)
            
        can.meanCansatRSSI=np.mean(can.LogCansatRSSI)
        can.meanLostRSSI=np.mean(can.LogLostRSSI)
        print('---mean---')
        print(can.meanCansatRSSI)
        print(can.meanLostRSSI)
        can.n_LogCansatRSSI.append(can.LogCansatRSSI)
        can.n_LogLostRSSI.append(can.LogLostRSSI)
        print('---log---')
        print(can.n_LogCansatRSSI)
        print(can.n_LogLostRSSI)
        i+=1
except KeyboardInterrupt:
    print('finished')
    can.keyboardinterrupt()
    GPIO.cleanup()
    
