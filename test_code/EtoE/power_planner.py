"""
power_plannerに1フレーム与えると以下の形で出力の指令を返します。
{"R":power_R,"L":power_L}
それぞれ基準となる出力(STANDARD_POWER)に対して定義する出力範囲(±POWER_RANGE)で変動します。
速度と抽出する色の設定をしてください。
"""

import cv2
import numpy as np


class PowerPlanner():
    """
    指定した範囲の色の物体の座標を取得する関数
    frame: 画像
    AREA_RATIO_THRESHOLD: area_ratio未満の塊は無視する
    LOW_COLOR: 抽出する色の下限(h,s,v)
    HIGH_COLOR: 抽出する色の上限(h,s,v)
    """
    # 速度の設定
    STANDARD_POWER = 65
    POWER_RANGE = 15

    # 色の設定
    # 0 <= h <= 179 (色相)　OpenCVではmax=179なのでR:0(180),G:60,B:120となる
    # 0 <= s <= 255 (彩度)　黒や白の値が抽出されるときはこの閾値を大きくする
    # 0 <= v <= 255 (明度)　これが大きいと明るく，小さいと暗い
    #{1:red,0:yellow}
    # LOW_COLOR = {1:np.array([150, 150, 115]),0:np.array([25, 200, 180]),99:np.array([18, 227, 217])}
    # HIGH_COLOR = {1:np.array([179, 255, 255]),0:np.array([27, 255, 255]),99:np.array([21, 255, 255])}
    
    # LOW_COLOR = {0:np.array([[0, 64, 0],[150, 64, 0]]),1:np.array([100, 75, 75])}
    # HIGH_COLOR = {0:np.array([[10, 255, 255],[179, 255, 255]]),1:np.array([140, 255, 255])}

    #{1:red,0:blue,99:orange}
    LOW_COLOR = {1:np.array([150, 150, 115]),0:np.array([109, 200, 180]),99:np.array([18, 227, 217])}
    HIGH_COLOR = {1:np.array([179, 255, 255]),0:np.array([111, 255, 255]),99:np.array([21, 255, 255])}

    # 抽出する色の塊のしきい値
    AREA_RATIO_THRESHOLD = 0.00003
    def __init__(self):
        self.pos = []

    def find_specific_color(self,frame,AREA_RATIO_THRESHOLD,LOW_COLOR,HIGH_COLOR,connecting_state):
        # 高さ，幅，チャンネル数
        h,w,c = frame.shape

        # hsv色空間に変換
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        
        # 色を抽出する
        ex_img = cv2.inRange(hsv,LOW_COLOR[connecting_state],HIGH_COLOR[connecting_state])

        # 輪郭抽出
        # 変更点 < opencvのバージョンの違いにより？引数を少なく設定>
        #_,contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 面積を計算
        areas = np.array(list(map(cv2.contourArea,contours)))
        
        if len(areas) == 0 or np.max(areas) / (h*w) < AREA_RATIO_THRESHOLD:
            # 見つからなかったらNoneを返す
            try:
                print(np.max(areas) / (h*w) )
            except:
                print("no color")
            return None
        else:
            #print("@powerplanner\ncolor area = ",np.max(areas) / (h*w))
            # 面積が最大の塊の重心を計算し返す
            max_idx = np.argmax(areas)
            max_area = areas[max_idx]
            max_a = areas[max_idx]
            result = cv2.moments(contours[max_idx])
            x = int(result["m10"]/result["m00"])
            y = int(result["m01"]/result["m00"])
            return (x,y,max_area)
            
    # def find_specific_color(frame,AREA_RATIO_THRESHOLD,LOW_COLOR,HIGH_COLOR,connecting_state):
        # # 高さ，幅，チャンネル数
        # h,w,c = frame.shape

        # # hsv色空間に変換
        # hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        
        # # 色を抽出する
        # if connecting_state == 0:
            # ex_img1 = cv2.inRange(hsv,LOW_COLOR[connecting_state][0,:],HIGH_COLOR[connecting_state][0,:])
            # ex_img2 = cv2.inRange(hsv,LOW_COLOR[connecting_state][1,:],HIGH_COLOR[connecting_state][1,:])
            # ex_img = ex_img1 + ex_img2
        # else:
            # ex_img = cv2.inRange(hsv,LOW_COLOR[connecting_state],HIGH_COLOR[connecting_state])
        # # 輪郭抽出
        # # 変更点 < opencvのバージョンの違いにより？引数を少なく設定>
        # #_,contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # # 面積を計算
        # areas = np.array(list(map(cv2.contourArea,contours)))
        
        # if len(areas) == 0 or np.max(areas) / (h*w) < AREA_RATIO_THRESHOLD:
            # # 見つからなかったらNoneを返す
            # try:
                # print(np.max(areas) / (h*w) )
            # except:
                # print("no color")
            # return None
        # else:
            # print("@powerplanner\ncolor area = ",np.max(areas) / (h*w))
            # # 面積が最大の塊の重心を計算し返す
            # max_idx = np.argmax(areas)
            # max_area = areas[max_idx]
            # max_a = areas[max_idx]
            # result = cv2.moments(contours[max_idx])
            # x = int(result["m10"]/result["m00"])
            # y = int(result["m01"]/result["m00"])
            # return (x,y,max_area)


    def power_calculation(self,pos,h,w,flag):
        if not flag:
            xn = 2*(pos[0]+300-w/2) / w + 0.00000001 ### + 300 ireru no kottijanai??
            power_R = int(self.STANDARD_POWER - self.POWER_RANGE * xn)
            power_L = int(self.STANDARD_POWER + self.POWER_RANGE * xn+5)
        else:
            xn = 2*(pos[0]-w/2) / w + 0.00000001
            power_R = -int(xn/abs(xn)*(self.STANDARD_POWER*1.15 + self.POWER_RANGE * abs(xn))) ### +- ga umareru youni
            power_L = -power_R+int(xn/abs(xn))*7
        w_rate = abs(xn) ### sleep zikan keisan you
        return power_R,power_L,w_rate

    """
    def power_calculation(self.pos,h,w):
        power_R = 0
        power_L = 0
        if pos[0] > 4*w/5:
            power_R = 30
            power_L = 50
        elif pos[0] > 3*w/5:
            power_R = 35
            power_L = 45
        elif pos[0] > 2*w/5:
            power_R = 40
            power_L = 40
        elif pos[0] > 1*w/5:
            power_R = 45
            power_L = 35
        else:
            power_R = 50
            power_L = 30    
        return power_R,power_L
    """

    def power_planner(self,frame,connecting_state,ar_count=0):
        """
        arg:
            frame
        return:
            {"R":power_R,"L":power_L,"Clear":bool} 
        """
        move = 'stop'
        height, width = frame.shape[:2]

        aprc_clear = False #これは目標に到達できたかのbool値

        self.pos = self.find_specific_color(
                frame,
                self.AREA_RATIO_THRESHOLD,
                self.LOW_COLOR,
                self.HIGH_COLOR,
                connecting_state
            )
        
        if self.pos is not None:
            detected = True
            if connecting_state == 0:
                if self.pos[2] > 6000:
                    aprc_clear = True #これは目標に到達できたかのbool値
            else:
                if self.pos[2] > 10000:
                # arm temae : 28000
                # arm red : 25000
                    aprc_clear = True #これは目標に到達できたかのbool値
            if ar_count > 0:
                aprc_clear = True
            print("aprc_clear : ",aprc_clear)
            power_R, power_L, w_rate = self.power_calculation(self.pos,height,width,aprc_clear)
            
        else:
            self.pos = ["none","none","none"]
            move = 'stop'
            power_R, power_L = 0,0
            w_rate = None ### mienai toki ni None ni naruyouni
            detected = False
        return {"R":power_R,"L":power_L,"Clear":aprc_clear,"Detected_tf":detected,"w_rate":w_rate,"move":move} ### sleep zikan keisan ni motiiru node w_rate wo dasu

    def para_detection(self,frame):
        height, width = frame.shape[:2]

        self.pos = self.find_specific_color(
                frame,
                self.AREA_RATIO_THRESHOLD,
                self.LOW_COLOR,
                self.HIGH_COLOR,
                99
            )
        
        aprc_clear = True
        move = 'stop'
        
        if self.pos is not None:
            if self.pos[2] > 6000:
                detected = True
                power_L, power_R, w_rate = self.power_calculation(self.pos,height,width,aprc_clear)
                if power_L > power_R:
                    move = 'stay-right'
                else:
                    move = 'stay-left'
            else:
                move = 'stop'
                power_R, power_L = 0,0
                w_rate = None ### mienai toki ni None ni naruyouni
                detected = False
        else:
            self.pos = ["none","none","none"]
            move = 'stop'
            print("here")
            power_R, power_L = 0,0
            w_rate = None ### mienai toki ni None ni naruyouni
            detected = False

        return {"R":power_R,"L":power_L,"Clear":aprc_clear,"Detected_tf":detected,"w_rate":w_rate,"move":move} ### sleep zikan keisan ni motiiru node w_rate wo dasu
