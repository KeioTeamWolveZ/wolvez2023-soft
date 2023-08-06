from tkinter_test import Tkmain
import RPi.GPIO as GPIO

if __name__ == '__main__':
    try:
        tk = Tkmain()
        tk.scale_and_button()
        tk.tkstart()
        tk.tkstop()
    except KeyboardInterrupt:
        tk.tkstop()
        GPIO.cleanup()
