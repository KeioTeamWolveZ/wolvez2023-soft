
import cv2
import numpy as np

class PowerPlanner_cansat():

    def __init__(self):
        self.id_size = {1:1,2:2.5,3:2.5,4:1,5:1,6:1,7:2.5,8:2.5,9:1,10:1}
        # 速度の設定
        self.STANDARD_POWER_COLOR = 40
        self.STANDARD_POWER_AR = 30
        self.POWER_RANGE = 10
        # 色の設定
        # 0 <= h <= 179 (色相)　OpenCVではmax=179なのでR:0(180),G:60,B:120となる
        # 0 <= s <= 255 (彩度)　黒や白の値が抽出されるときはこの閾値を大きくする
        # 0 <= v <= 255 (明度)　これが大きいと明るく，小さいと暗い
        # ここでは青色を抽出するので120±20を閾値とした
        self.LOW_COLOR = np.array([100, 75, 75])
        self.HIGH_COLOR = np.array([140, 255, 255])
        # 抽出する青色の塊のしきい値
        self.AREA_RATIO_THRESHOLD = 0.005
        # ARマーカー検出判定
        self.aprc_c = False


    def find_specific_color(self,frame,AREA_RATIO_THRESHOLD,LOW_COLOR,HIGH_COLOR):
        # 高さ，幅，チャンネル数
        h,w,c = frame.shape

        # hsv色空間に変換
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        
        # 色を抽出する
        ex_img = cv2.inRange(hsv,LOW_COLOR,HIGH_COLOR)

        # 輪郭抽出
        # 変更点 < opencvのバージョンの違いにより？引数を少なく設定>
        #_,contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 面積を計算
        areas = np.array(list(map(cv2.contourArea,contours)))

        if len(areas) == 0 or np.max(areas) / (h*w) < AREA_RATIO_THRESHOLD:
            # 見つからなかったらNoneを返す
            # print("the area is too small")
            return None
        else:
            # 面積が最大の塊の重心を計算し返す
            max_idx = np.argmax(areas)
            max_area = areas[max_idx]
            max_a = areas[max_idx]
            result = cv2.moments(contours[max_idx])
            x = int(result["m10"]/result["m00"])
            y = int(result["m01"]/result["m00"])
            return (x,y,max_area)


    def power_calculation(self,pos,h,w):
        
        xn = 2*(pos[0]-w/2) / w
        power_R = int(self.STANDARD_POWER_COLOR - self.POWER_RANGE * xn)
        power_L = int(self.STANDARD_POWER_COLOR + self.POWER_RANGE * xn)
        
        return power_R,power_L
    
    def Color_power_planner(self,frame):
        height, width = frame.shape[:2]

        aprc_clear = False #これは目標に到達できたかのbool値

        pos = self.find_specific_color(
                frame,
                self.AREA_RATIO_THRESHOLD,
                self.LOW_COLOR,
                self.HIGH_COLOR
            )
        
        if pos is not None:
            power_R, power_L = self.power_calculation(pos,height,width)
            detected = True
            if pos[2] > 7000:
                aprc_clear = True #これは目標に到達できたかのbool値
            
        else:
            power_R, power_L = 0,0
            detected = False
        return {"R":power_R,"L":power_L,"Clear":aprc_clear,"Detected_tf":detected}



    def AR_powerplanner(self,ar_info:dict={"1":{"x":0, "y":3, "z":5} ,"2":{"x":1, "y":0, "z":7} ,"3":{"x":0, "y":0, "z":0}}) -> dict:
        
        # 速度の設定
        self.STANDARD_POWER = 30
        self.POWER_RANGE = 10

        marker_1 = np.array([ar_info["1"]["x"],ar_info["1"]["y"],ar_info["1"]["z"]])
        marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
        vec, distance = self.__targetting(marker_1,marker_2)
        if distance > -0.5:
            if distance > 0.5:
                '''
                接近するまでは連続的に近づく(アームとモジュールが横並びするまで？)
                '''
                power_R = int(self.STANDARD_POWER_AR + self.POWER_RANGE * distance)
                power_L = int(self.STANDARD_POWER_AR - self.POWER_RANGE * distance)

            else:
                '''
                接近後なので回転したい：要検討
                '''
                power_R = int(self.POWER_RANGE * vec(0))
                power_L = int(-1 * self.POWER_RANGE * vec(0))

        else:
            '''
            distanceが負のときバックする？
            '''
            power_R = int(-1*self.STANDARD_POWER_AR - self.POWER_RANGE * distance)
            power_L = int(-1*self.STANDARD_POWER_AR + self.POWER_RANGE * distance)
        
        return {"R":power_R,"L":power_L,"C":self.aprc_c}

    def __targetting(self,marker_1:np.ndarray=np.zeros(3), marker_2:np.ndarray=np.zeros(3)):
        '''
        二つのベクトルの差分と閾値に対する評価を出力
        '''
        target_vec = marker_2 - marker_1
        #print(target_vec)
        distance = (target_vec[2]/abs(target_vec[2]))*(target_vec[0]**2 + target_vec[2]**2)**0.5 
        return target_vec, distance

