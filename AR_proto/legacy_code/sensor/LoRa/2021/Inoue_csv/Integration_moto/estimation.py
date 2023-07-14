import RPi.GPIO as GPIO
import sys
import time
import math
import numpy as np

class estimation():
    def __init__(self,pin_a,pin_b,pin_c,pin_d): #各ピンのセットアップ
        GPIO.setmode(GPIO.BCM)
        
        #motorR set up
        GPIO.setup(pin_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.pin_a = pin_a 
        self.pin_b = pin_b
        
        self.angle=0.
        self.prev_angle=0.
        self.prev_data=0
        self.delta=360./15
        self.enc_time=[]
        self.enc_del_time=[]
        self.enc_ave_time=0
        self.mot_speed=0 #motor-revolution/sec
        
        GPIO.add_event_detect(self.pin_a,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_b,GPIO.BOTH)
        
        #motorL set up
        
        GPIO.setup(pin_c, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_d, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        self.pin_c = pin_c
        self.pin_d = pin_d
        
        self.angle2=0.
        self.prev_angle2=0.
        self.prev_data2=0
        self.delta2=360./15
        self.enc_time2=[]
        self.enc_del_time2=[]
        self.enc_ave_time2=0
        self.mot_speed2=0 #motor-revolution/sec
        
        GPIO.add_event_detect(self.pin_c,GPIO.BOTH)
        GPIO.add_event_detect(self.pin_d,GPIO.BOTH)
        
        self.cansat_speed = 0 
        self.cansat_rad_speed = 0
        
    
    def callback(self, gpio_pin1, gpio_pin2):
        self.mot_speed=0
        self.mot_speed2=0
        
        while self.mot_speed==0:
            self.current_a=GPIO.input(self.pin_a)
            self.current_b=GPIO.input(self.pin_b)
            
            self.encoded=(self.current_a<<1)|self.current_b
            sum=(self.prev_data<<2)|self.encoded
        
            if sum==0b0010:
                self.enc_time.append(time.time())
            
            if len(self.enc_time)==1000:
                for i in range(0,len(self.enc_time)-1):
                    self.enc_del_time.append(0)
                for i in range(0,len(self.enc_time)-1):
                    self.enc_del_time[i]=self.enc_time[i+1]-self.enc_time[i]
                
                self.enc_ave_time=np.mean(self.enc_del_time)
                self.mot_speed=1/(898*self.enc_ave_time)
                    
                #print("motor-revolution/sec",self.mot_speed)
                self.enc_time=[]
                self.enc_del_time=[]
            
            self.prev_data=self.encoded
            self.prev_angle = self.angle
        
        while self.mot_speed2==0:
            self.current_c=GPIO.input(self.pin_c)
            self.current_d=GPIO.input(self.pin_d)
            
            self.encoded2=(self.current_c<<1)|self.current_d
            sum=(self.prev_data2<<2)|self.encoded2
        
            if sum==0b0010:
                self.enc_time2.append(time.time())
            
            if len(self.enc_time2)==1000:
                for i in range(0,len(self.enc_time2)-1):
                    self.enc_del_time2.append(0)
                for i in range(0,len(self.enc_time2)-1):
                    self.enc_del_time2[i]=self.enc_time2[i+1]-self.enc_time2[i]
                
                self.enc_ave_time2=np.mean(self.enc_del_time2)
                self.mot_speed2=1/(898*self.enc_ave_time2)
                    
                #print("motor-revolution/sec",self.mot_speed)
                self.enc_time2=[]
                self.enc_del_time2=[]
            
            self.prev_data2=self.encoded2
            self.prev_angle2 = self.angle2
        
        return self.mot_speed, self.mot_speed2
    
    def callback2(self, gpio_pin1, gpio_pin2):
        self.mot_speed=0
        self.mot_speed2=0
        self.pulse=898
        self.keisan = 1
        self.keisan2 = 1
        self.hantei = 0
        self.kaiten1=0
        self.kaiten2=0
        
        while self.keisan<=5:
            self.current_a=GPIO.input(self.pin_a)
            self.current_b=GPIO.input(self.pin_b)
            
            self.encoded=(self.current_a<<1)|self.current_b
            sum=(self.prev_data<<2)|self.encoded
        
            if sum==0b0010:
                self.enc_time.append(time.time())
                self.kaiten1=1
            elif sum==0b1000:
                self.enc_time.append(time.time())
                self.kaiten1=2
            
            if len(self.enc_time)==self.pulse:
                #print("motor-revolution/sec",self.mot_speed)
                self.enc_time=[]
                self.keisan = self.keisan + 1
#                 self.enc_del_time=[]
            
            self.prev_data=self.encoded
            self.prev_angle = self.angle
        
        while self.keisan2<=5:
            self.current_c=GPIO.input(self.pin_c)
            self.current_d=GPIO.input(self.pin_d)
            
            self.encoded2=(self.current_c<<1)|self.current_d
            sum=(self.prev_data2<<2)|self.encoded2
        
            if sum==0b0010:
                self.enc_time2.append(time.time())
                self.kaiten2=1
            elif sum==0b1000:
                self.enc_time2.append(time.time())
                self.kaiten2=2
            
            if len(self.enc_time2)==self.pulse:
                #print("motor-revolution/sec",self.mot_speed)
                self.enc_time2=[]
                self.keisan2 = self.keisan2 + 1
#                 self.enc_del_time=[]
            
            self.prev_data2=self.encoded2
            self.prev_angle2 = self.angle2
            
        self.hantei=1
        
        return self.hantei
    
    def est_v_w(self, gpio_pin1, gpio_pin2):
        self.mot_speed=0
        self.mot_speed2=0
        self.pulse=898
        self.iteration=300
        self.kaiten1=0
        self.kaiten2=0
    
        while self.mot_speed==0:
            self.current_a=GPIO.input(self.pin_a)
            self.current_b=GPIO.input(self.pin_b)
            
            self.encoded=(self.current_a<<1)|self.current_b
            sum=(self.prev_data<<2)|self.encoded
#             print(0)
            if sum==0b0010:
                self.enc_time.append(time.time())
                self.kaiten1=1
            elif sum==0b1000:
                self.enc_time.append(time.time())
                self.kaiten1=2
#                 print(1)
            if len(self.enc_time)==self.iteration:
#                 print(2)
                for i in range(0,len(self.enc_time)-1):
                    self.enc_del_time.append(0)
                for i in range(0,len(self.enc_time)-1):
                    self.enc_del_time[i]=self.enc_time[i+1]-self.enc_time[i]
                
                self.enc_ave_time=np.mean(self.enc_del_time)
                if self.kaiten1==1:
                    self.mot_speed=1/(self.pulse*self.enc_ave_time)
                elif self.kaiten1==2:
                    self.mot_speed=-1/(self.pulse*self.enc_ave_time)
                    
                #print("motor-revolution/sec",self.mot_speed)
                self.enc_time=[]
                self.enc_del_time=[]
            
            self.prev_data=self.encoded
            self.prev_angle = self.angle
        
        while self.mot_speed2==0:
            self.current_c=GPIO.input(self.pin_c)
            self.current_d=GPIO.input(self.pin_d)
            
            self.encoded2=(self.current_c<<1)|self.current_d
            sum=(self.prev_data2<<2)|self.encoded2
        
            if sum==0b0010:
                self.enc_time2.append(time.time())
                self.kaiten2=1
            elif sum==0b1000:
                self.enc_time2.append(time.time())
                self.kaiten2=2
            if len(self.enc_time2)==self.iteration:
                for i in range(0,len(self.enc_time2)-1):
                    self.enc_del_time2.append(0)
                for i in range(0,len(self.enc_time2)-1):
                    self.enc_del_time2[i]=self.enc_time2[i+1]-self.enc_time2[i]
                
                self.enc_ave_time2=np.mean(self.enc_del_time2)
                if self.kaiten2==1:
                    self.mot_speed2=1/(self.pulse*self.enc_ave_time2)
                elif self.kaiten2==2:
                    self.mot_speed2=-1/(self.pulse*self.enc_ave_time2)
                    
                #print("motor-revolution/sec",self.mot_speed)
                self.enc_time2=[]
                self.enc_del_time2=[]
            
            self.prev_data2=self.encoded2
            self.prev_angle2 = self.angle2
        
        self.cansat_speed = 2*3.14*(0.0665/2)*self.mot_speed + 2*3.14*(0.0665/2)*self.mot_speed2
        self.cansat_rad_speed = (0.0665/0.196)*self.mot_speed - (0.0665/0.196)*self.mot_speed2
        
        return self.cansat_speed, self.cansat_rad_speed
    
    def est_v_w_for_c(self, gpio_pin1, gpio_pin2):
        self.mot_speed=0
        self.mot_speed2=0
        self.pulse=871
        self.iteration=30
        
        while self.mot_speed==0:
            self.current_a=GPIO.input(self.pin_a)
            self.current_b=GPIO.input(self.pin_b)
            
            self.encoded=(self.current_a<<1)|self.current_b
            sum=(self.prev_data<<2)|self.encoded
        
            if sum==0b0010:
                self.enc_time.append(time.time())
            
            if len(self.enc_time)==self.iteration:
                for i in range(0,len(self.enc_time)-1):
                    self.enc_del_time.append(0)
                for i in range(0,len(self.enc_time)-1):
                    self.enc_del_time[i]=self.enc_time[i+1]-self.enc_time[i]
                
                self.enc_ave_time=np.mean(self.enc_del_time)
                self.mot_speed=1/(self.pulse*self.enc_ave_time)
                    
                #print("motor-revolution/sec",self.mot_speed)
                self.enc_time=[]
                self.enc_del_time=[]
            
            self.prev_data=self.encoded
            self.prev_angle = self.angle
        
        self.cansat_speed = 2*3.14*(0.0665/2)*self.mot_speed + 2*3.14*(0.0665/2)*0
        self.cansat_rad_speed = (0.0665/0.196)*self.mot_speed - (0.0665/0.196)*0
        
        return self.cansat_speed, self.cansat_rad_speed
    
    def odometri(self,v,w,t,x,y,q):
        x_new=x+v*t*math.cos(q)
        y_new=y+v*t*math.sin(q)
        q_new=q+w*t
        
        return x_new,y_new,q_new
