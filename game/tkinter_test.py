from tkinter import *
from tkinter import ttk

from motor import Motor
from arm import Arm

class Tkmain():
    __run = False
    def __init__(self):
        GPIO.setwarnings(False)
        self.MotorR = motor.motor(6,5,13)
        self.MotorL = motor.motor(20,16,12)
        self.arm = Arm(23)
        
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
            command=lambda e: print('val:%4d' % self.val.get()))
        self.sc.grid(row=2, column=0, sticky=(N, E, S, W))
        self.style = ttk.Style()
        self.style.configure("office.TButton", font=20, anchor="s")

        # Button
        self.faster = ttk.Button(
            self.frame,
            text='はやい',
            width=10,
            style="office.TButton",
            command=lambda: self.val)
            # command=lambda: print('val:%4d' % self.val.get()))
        self.faster.grid(row=0, column=0, padx=5, sticky=(E))

        # Button
        self.slower = ttk.Button(
            self.frame,
            text='おそい',
            width=10,
            style="office.TButton",
            command=lambda: self.__go())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.slower.grid(row=4, column=0, padx=5, sticky=(E))

        # Button
        self.go = ttk.Button(
            self.frame,
            text='走る/止まる',
            width=10,
            style="office.TButton",
            command=lambda: self.__go())
            # command=lambda: print('val:%4d' % self.val.get()))
        self.go.grid(row=1, column=2, padx=5, sticky=(E))

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

    def vup(self):
        if self.val.get() < 90:
            self.val.value = self.val.get() + 10
        else:
            self.val.value = 100

    def printer(self,a):
        print(a)

    def tkstart(self):
        self.root.mainloop()

    def __go(self):
        if not self.__run:
            MotorR.go(float(self.val.get()))
            MotorL.go(float(self.val.get()))
        else:
            MotorR.stop()
            MotorL.stop()

    def __back(self):
        MotorR.back(60)
        MotorL.back(60)
        time.sleep(0.05)
        MotorR.stop()
        MotorL.stop()

    def __right(self):
        MotorR.go(-float(self.val.get()))
        MotorL.go(float(self.val.get()))
        time.sleep(0.05)
        MotorR.stop()
        MotorL.stop()

    def __left(self):
        MotorR.go(float(self.val.get()))
        MotorL.go(-float(self.val.get()))
        time.sleep(0.05)
        MotorR.stop()
        MotorL.stop()

if __name__ == '__main__':
    tk = Tkmain()
    tk.scale_and_button()
    tk.tkstart()
    print(tk.val.get())