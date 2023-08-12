from tkinter import *
from tkinter import ttk
import time

from motor import Motor
from arm import Arm

import RPi.GPIO as GPIO

class Tkmain():
    __run = False
    __arm = True
    def __init__(self):
        GPIO.setwarnings(False)
        self.MotorL = Motor(6,5,13)
        self.MotorR = Motor(20,16,12)
        self.arm = Arm(23)
        self.arm.setup()
        self.arm.up()
        
        self.root = Tk()
        self.root.title('CONTROLLER')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Frame
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.grid(sticky=(N, W, S, E))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

    def scale_and_button(self):

        # スケールの作成
        self.val = DoubleVar()
        self.sc = ttk.Scale(
            self.frame,
            variable=self.val,
            orient=VERTICAL,
            length=200,
            from_=100,
            to=50,
            command=lambda e: print('速度:%4d' % self.val.get()))
        self.sc.grid(row=2, column=0, sticky=(N, E, S, W))
        self.style = ttk.Style()
        self.style.configure("office.TButton", font=20, anchor="s")
        self.val.set(50)

        # textbox
        self.textbox = ttk.Label(
            self.frame,
            text='( ◜ω◝ )',
            width=10)
            # command=lambda: print('val:%4d' % self.val.get()))
        self.textbox.grid(row=5, column=2, padx=5, sticky=(E))

        # スケールの作成
        self.val_arm = DoubleVar()
        self.sc_arm = ttk.Scale(
            self.frame,
            variable=self.val_arm,
            orient=VERTICAL,
            length=200,
            from_=1650,
            to=950,
            command=self.hset)
        self.sc_arm.grid(row=2, column=4, sticky=(N, E, S, W))
        self.style = ttk.Style()
        self.style.configure("office.TButton", font=20, anchor="s")
        self.val_arm.set(1650)

        # Button
        self.faster = ttk.Button(
            self.frame,
            text='はやい',
            width=10,
            style="office.TButton",
            command=lambda: self.vup())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.faster.grid(row=0, column=0, padx=5, sticky=(E))

        # Button
        self.slower = ttk.Button(
            self.frame,
            text='おそい',
            width=10,
            style="office.TButton",
            command=lambda: self.vdown())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.slower.grid(row=4, column=0, padx=5, sticky=(E))

        # Button (Added by kazu)
        self.upward = ttk.Button(
            self.frame,
            text='上げる',
            width=10,
            style="office.TButton",
            command=lambda: self.hup())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.upward.grid(row=0, column=4, padx=5, sticky=(E))

        # Button (Added by kazu)
        self.downward = ttk.Button(
            self.frame,
            text='下げる',
            width=10,
            style="office.TButton",
            command=lambda: self.hdown())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.downward.grid(row=4, column=4, padx=5, sticky=(E))
        
        # Button
        self.go = ttk.Button(
            self.frame,
            text='走る/止まる',
            width=10,
            style="office.TButton",
            command=lambda: self.__go())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.go.grid(row=0, column=2, padx=5, sticky=(E))

        # Button
        self.go_a_little = ttk.Button(
            self.frame,
            text='少し走る',
            width=10,
            style="office.TButton",
            command=lambda: self.__go_a_little())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.go_a_little.grid(row=1, column=2, padx=5, sticky=(E))
        
        # Button
        self.back = ttk.Button(
            self.frame,
            text='うしろ',
            width=10,
            style="office.TButton",
            command=lambda: self.__back())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.back.grid(row=3, column=2, padx=5, sticky=(E))

        # Button
        self.right = ttk.Button(
            self.frame,
            text='みぎ',
            width=10,
            style="office.TButton",
            command=lambda: self.__right())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.right.grid(row=2, column=3, padx=5, sticky=(E))

        # Button
        self.left = ttk.Button(
            self.frame,
            text='ひだり',
            width=10,
            style="office.TButton",
            command=lambda: self.__left())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.left.grid(row=2, column=1, padx=5, sticky=(E))
        
        # Button
        self.grasp = ttk.Button(
            self.frame,
            text='TRY!!',
            width=10,
            style="office.TButton",
            command=lambda: self.__arm_updown())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.grasp.grid(row=2, column=2, padx=5, sticky=(E))

        # Button (added by kazu)
        self.picture = ttk.Button(
            self.frame,
            text='写真',
            width=10,
            style="office.TButton",
            command=lambda: self.__picture())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.picture.grid(row=1, column=3, padx=5, sticky=(E))

        # Button (added by kazu)
        self.dance = ttk.Button(
            self.frame,
            text='踊る',
            width=10,
            style="office.TButton",
            command=lambda: self.__dance())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.dance.grid(row=1, column=1, padx=5, sticky=(E))


        # Button (added by kazu)
        self.finish = ttk.Button(
            self.frame,
            text='終わる',
            width=10,
            style="office.TButton",
            command=lambda: self.__finish())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.finish.grid(row=3, column=3, padx=5, sticky=(E))

    def vup(self):
        if self.val.get() < 90:
            self.val.set(self.val.get() + 10)
        else:
            self.val.set(100)
        print('速度:%4d' % self.val.get())
        self.textbox["text"]='速度:%4d' % self.val.get()
            
    def vdown(self):
        if self.val.get() > 60:
            self.val.set(self.val.get() - 10)
        else:
            self.val.set(50)
        print('速度:%4d' % self.val.get())
        self.textbox["text"]='速度:%4d' % self.val.get()

    def hup(self):
        if self.val_arm.get() < 1600:
            self.val_arm.set(self.val_arm.get() + 50)
        else:
            self.val_arm.set(1650)
        print('高さ:%4d' % self.val_arm.get())
        self.textbox["text"]='wait a second'
        self.arm.move(self.val_arm.get())
        self.textbox["text"]='高さ:%4d' % self.val_arm.get()
            
    def hdown(self):
        if self.val_arm.get() > 1000:
            self.val_arm.set(self.val_arm.get() - 50)
        else:
            self.val_arm.set(950)
        print('高さ:%4d' % self.val_arm.get())
        self.textbox["text"]='wait a second'
        self.arm.move(self.val_arm.get())
        self.textbox["text"]='高さ:%4d' % self.val_arm.get()

    def hset(self,var):
        try:
            value=int(var[:4])
        except ValueError:
            value=int(var[:3])
        self.val_arm.set(value)
        self.arm.move(value)
        self.textbox["text"]='高さ:%4d' % self.val_arm.get()

    
    def __arm_updown(self):
        # if not self.__arm:
            # self.__arm = True
            # print("ARM UP!")
            # self.arm.up()
        # else:
            # self.__arm = False
            # print("ARM DOWN!")
            # self.arm.down()
        self.textbox["text"]='!ATTACK!'
        self.textbox.update()
        self.arm.down()
        time.sleep(1)
        self.arm.up()
        self.textbox["text"]='高さ:%4d' % self.val_arm.get()

    def __go(self):
        if not self.__run:
            print("RUN!")
            self.__run = True
            self.textbox["text"]='RUN 速度:%4d' % self.val.get()
            self.MotorR.go(float(self.val.get()))
            self.MotorL.go(float(self.val.get()))
        else:
            print("STOP!")
            self.__run = False
            self.MotorR.stop()
            self.MotorL.stop()
            self.textbox["text"]='STOP!'
        # self.arm.up()
        self.arm.move(self.val_arm.get())

    def __go_a_little(self):
        print("RUN just a little bit!")
        self.MotorR.go(60)
        self.MotorL.go(60)
        time.sleep(0.05)
        self.MotorR.stop()
        self.MotorL.stop()
        # self.arm.up()
        self.arm.move(self.val_arm.get())
        self.textbox["text"]='少し走る'

    def __back(self):
        print("BACK!")
        self.MotorR.back(60)
        self.MotorL.back(60)
        time.sleep(0.05)
        self.MotorR.stop()
        self.MotorL.stop()
        # self.arm.up()
        self.arm.move(self.val_arm.get())
        self.textbox["text"]='うしろ'

    def __right(self):
        print("TURN RIGHT!")
        self.MotorR.back(float(self.val.get()))
        self.MotorL.go(float(self.val.get()))
        time.sleep(0.05)
        self.MotorR.stop()
        self.MotorL.stop()
        # self.arm.up()
        self.arm.move(self.val_arm.get())
        self.textbox["text"]='みぎ'

    def __left(self):
        print("TURN LEFT!")
        self.MotorR.go(float(self.val.get()))
        self.MotorL.back(float(self.val.get()))
        time.sleep(0.05)
        self.MotorR.stop()
        self.MotorL.stop()
        # self.arm.up()
        self.arm.move(self.val_arm.get())
        self.textbox["text"]='ひだり'
        
    def __finish(self):
        print("finish the game!")
        self.MotorR.stop()
        self.MotorL.stop()
        # self.arm.up()
        self.arm.move(self.val_arm.get())
        self.root.destroy()
        
    def __dance(self):
        print("ଘ (੭*ˊᵕˋ)੭*")
        self.textbox["text"]='ଘ (੭*ˊᵕˋ)੭*'
        self.textbox.update()
        self.arm.down()
        time.sleep(0.8)
        print("٩(ˊᗜˋ*)و")
        self.textbox["text"]='٩(ˊᗜˋ*)و'
        self.textbox.update()
        self.arm.up()
        time.sleep(0.8)
        print("ଘ (੭*ˊᵕˋ)੭*")
        self.textbox["text"]='ଘ (੭*ˊᵕˋ)੭*'
        self.textbox.update()
        self.arm.down()
        time.sleep(0.8)
        print("٩(ˊᗜˋ*)و")
        self.textbox["text"]='٩(ˊᗜˋ*)و'
        self.textbox.update()
        self.arm.up()
        time.sleep(0.8)
        print("(‘ω’ )三")
        self.textbox["text"]='(‘ω’ )三'
        self.textbox.update()
        self.MotorR.back(float(self.val.get()))
        self.MotorL.go(float(self.val.get()))
        time.sleep(1.5)
        print("三( ‘ω’)")
        self.textbox["text"]='三( ‘ω’)'
        self.textbox.update()
        self.MotorR.go(float(self.val.get()))
        self.MotorL.back(float(self.val.get()))
        time.sleep(1.5)
        print("(‘ω’ )三")
        self.textbox["text"]='(‘ω’ )三'
        self.textbox.update()
        self.MotorR.back(float(self.val.get()))
        self.MotorL.go(float(self.val.get()))
        time.sleep(1.5)
        print("三( ‘ω’)")
        self.textbox["text"]='三( ‘ω’)'
        self.textbox.update()
        self.MotorR.go(float(self.val.get()))
        self.MotorL.back(float(self.val.get()))
        time.sleep(1.5)
        self.MotorR.stop()
        self.MotorL.stop()
        print("ヾ(*´∀｀*)ﾉ ")
        self.textbox["text"]='ヾ(*´∀｀*)ﾉ '
        self.textbox.update()
        
    def __picture(self):
        print("This function will be implemented by Yuma soon (｢･ω･)｢")
        self.textbox["text"]='(｢･ω･)｢ '
        self.textbox.update()
        
    def tkstart(self):
        self.root.mainloop()

    def tkstop(self):
        self.MotorR.stop()
        self.MotorL.stop()
        time.sleep(0.5)
        GPIO.cleanup()
        

if __name__ == '__main__':
    tk = Tkmain()
    tk.scale_and_button()
    tk.tkstart()
    tk.tkstop()
