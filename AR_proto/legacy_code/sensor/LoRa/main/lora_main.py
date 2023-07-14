import time
import lora


lora = lora.lora()

try:
    while True:
        lora.sendData("a")
        time.sleep(5)
    
except KeyboardInterrupt:
    print("Finished")
    lora.keyboardinterrupt()
    GPIO.cleanup()
    