import numpy as np
import cv2

from numpy import sin, cos, arccos

class ARPowerPlanner():

    #速度の設定
    STANDARD_POWER = 90
    POWER_RANGE = 10

    def __init__(self):
        self.arm_id = "1"
        # 各マーカーに対するxg,yg,zg
        self.marker_goal = {"2":[0.0,0.025,-0.023],"3":[0,0.001,0.038],"4":[0.0,0.042,-0.005],"5":[0,0.042,-0.005],\
            "6":[0,0.042,-0.005],"7":[0,0.043,-0.01],"11":[0.0,0.025,-0.0165],"16":[0.014,0.0105,0.022],"68":[-0.005,0.01,-0.055]}

    def goal(self,ar_info,id):
        """
        arg : 
            ar_info = {'x':x,'y':y,'z':z,'roll':roll,'pitch':pitch,'yaw':yaw,'norm':norm}
        return:
            Xg,Yg,Zg : カメラ座標系におけるゴール座標
        """

        x = ar_info[id]['x'] 
        y = ar_info[id]['y']
        z = ar_info[id]['z']
        roll = ar_info[id]['roll']
        pitch = ar_info[id]['pitch']
        yaw = ar_info[id]['yaw']
        rvec = ar_info[id]['rvec']
        bias = self.marker_goal[id] # マーカーからゴールまでのベクトル

        goal = self.rot_vec(rvec,bias)+np.array([[x],[y],[z]])
        goal= goal.T
        
        return goal.reshape(1,3)
    
    def rot_vec(self,rvec,vec):
        rvec_matrix = cv2.Rodrigues(rvec)
        rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し
        g = np.dot((rvec_matrix),vec).reshape(-1, 1)
        return g
        
    # def arm_ref(self,goal_y):
        # if self.connecting_state == 0:
            # normal_y = 0.00324128
            # a_high_x = 0.5326995111489172
            # b_high_x = -0.025198152589482
            # a_high_z = 0.3007670676823178
            # b_high_z = -0.05713972299054073
            # a_low_x = 0.8948315595389549
            # b_low_x = -0.017355877276581146
            # a_low_z = -0.10133101696485919
            # b_low_z = 0.04069127582154732
        # else:
            # normal_y = -0.01904927
            # a_high_x = 0.6571145219203942
            # b_high_x = -0.02929475486492132
            # a_high_z = 0.47718110056167956
            # b_high_z = -0.09062050520170216
            # a_low_x = 0.5769225937464898
            # b_low_x = -0.018491211975063995
            # a_low_z = 0.46703847010300253
            # b_low_z = -0.07648348582896586

        
        # if goal_y > normal_y:
            # marker_1 = np.array([a_high_x*goal_y + b_high_x, goal_y,a_high_z*goal_y + b_high_z])
        # else:
            # marker_1 = np.array([a_low_x*goal_y + b_low_x, goal_y,a_low_z*goal_y + b_low_z])
        # return marker_1

    def goalvec_maker(self,ar_info,goal_point,connecting_state,id):
        """
        def arm_orbit(x1,x2,y1,y2,goal_y):
        a = (x1-x2)/(y1-y2)
        b = y1 - a*x1
        return a*goal_y + b 
        """
        self.connecting_state = connecting_state
        if connecting_state == 0:
            if self.arm_id in ar_info.keys():
                marker_1 = np.array([ar_info[self.arm_id]["x"],ar_info[self.arm_id]["y"],ar_info[self.arm_id]["z"]])
            else:
                # marker_1 = np.array([0.0353238,0.00329190,0.15313373])
                # marker_1 = np.array([0.028160,0.0032412,0.144018])
                marker_1 = np.array([0.0168503,-0.0101923,0.1415139]) # スタビ変更
                # marker_1 = self.arm_ref(goal_point[0][1])
        else:
            # marker_1 = np.array([0.003606,-0.015277,0.138732])
            marker_1 = np.array([0.0139197,-0.0277264,0.1285234])
            # marker_1 = self.arm_ref(goal_point[0][1])
            # marker_1 = np.array([0.02100412,-0.01784624,0.130171312]) tansi zika
        vec, distance = self.__targetting(marker_1,goal_point)
        #print(f"vec:{vec[2]}")
        vec[1], vec[2] = self.calc_t_distance(id,ar_info, vec, distance) # new
        goal_area = {"x":[-0.004,0.004],"z":[-0.004,0.004]} # koko henka sasetai !!!!!!!!!!!
        # print(f"distance:{distance},vec:{vec}")
        print(f"vec:{vec}")

        return vec,goal_area

    def ar_powerplanner(self,ar_info,connecting_state,ar_checker):
        self.aprc_state = False # 2回目の接続の際にリセットできるようにしてある
        id = ar_checker["id"]
        goal_point = self.goal(ar_info,id)
        vec,goal_area = self.goalvec_maker(ar_info,goal_point,connecting_state,id)
        move = "stop"
        if vec[2] > goal_area["z"][0]:
            if vec[2] > goal_area["z"][1]:
                '''
                遠いVerは消した
                '''
                if vec[0] > goal_area["x"][0] and vec[0] < goal_area["x"][1]:
                    move = 'straight'
                    power_R = int(self.STANDARD_POWER - self.POWER_RANGE)
                    power_L = int(self.STANDARD_POWER - self.POWER_RANGE+5)
                else:
                    if vec[0] < goal_area["x"][0]:
                        move = 'straight-left'
                        power_R = int(self.STANDARD_POWER - self.POWER_RANGE )
                        power_L = int(0)
                    else:
                        move = 'straight-right'
                        power_R = int(0)
                        power_L = int(self.STANDARD_POWER - self.POWER_RANGE)
            else:
                # When z is satisfying the thresholds, cansat changes just orientation
                motor_ouput = self.STANDARD_POWER - self.POWER_RANGE
                if vec[0] > goal_area["x"][0] and vec[0] < goal_area["x"][1]:
                    print("Approach Finished")
                    power_R = 0
                    power_L = 0
                    self.aprc_state = True
                else:
                    if vec[0] < goal_area["x"][0]:
                        move = 'stay-left'
                        power_R = int(motor_ouput)
                        power_L = int(-motor_ouput)
                    else:
                        move = 'stay-right'
                        power_R = int(-motor_ouput)
                        power_L = int(motor_ouput)
                '''
                接近後なのでアーム動かしたい：要検討
                '''

        else:
            '''
            distanceが負のときバックする
            '''
            print("distance<0")
            move = 'back'
            power_R = int(-1*self.STANDARD_POWER)
            power_L = int(-1*self.STANDARD_POWER)

        return {"R":power_R,"L":power_L,"aprc_state":self.aprc_state,"move":move}

    def calc_t_distance(self,id,ar_info, vec, distance):
        if id == "16" or id == "3" or id == "68": # 68は裏面のマーカー、青モジュールに追加するマーカーも必要
            y_m = self.rot_vec(ar_info[id]['rvec'],[0,0,1])
        else:
            y_m = self.rot_vec(ar_info[id]['rvec'],[0,1,0])
        vec_normalize = vec.reshape(3,1)/np.linalg.norm(vec[1:3])
        #print(vec_normalize)
        cos_argment = np.dot(y_m[1:3].T,vec_normalize[1:3])
        #print(cos_argment)
        ultraman_wide = distance*np.sqrt(1-cos_argment**2)
        ultraman_height = abs(distance)*cos_argment #new
        return ultraman_wide[0][0],ultraman_wide[0][0]


    def __targetting(self,marker_1:np.ndarray=np.zeros(3), marker_2:np.ndarray=np.zeros(3)):
        '''
        二つのベクトルの差分と閾値に対する評価を出力
        '''
        target_vec = marker_2 - marker_1
        target_vec = target_vec[0]
        distance = np.sign(target_vec[2])*np.linalg.norm(target_vec[1:3])
        return target_vec, distance

#########################
### ColorPowerPlanner ###
#########################
class ColorPowerPlanner():
    """
    指定した範囲の色の物体の座標を取得する関数
    frame: 画像
    AREA_RATIO_THRESHOLD: area_ratio未満の塊は無視する
    LOW_COLOR: 抽出する色の下限(h,s,v)
    HIGH_COLOR: 抽出する色の上限(h,s,v)
    
    色の設定
    0 <= h <= 179 (色相)　OpenCVではmax=179なのでR:0(180),G:60,B:120となる
    0 <= s <= 255 (彩度)　黒や白の値が抽出されるときはこの閾値を大きくする
    0 <= v <= 255 (明度)　これが大きいと明るく，小さいと暗い
    """
    
    # Coefficient between ewbsite and numpy
    hsv_coef = np.array([1/2, 2.55, 2.55])
    
    # 速度の設定
    STANDARD_POWER = 65
    POWER_RANGE = 15

    #{1:red,0:blue,99:orange}
    # h:0~360, s:0~100, v:0~100
    
    ##orange
    LOW_COLOR_EDIT = {1:np.array([300, 59, 45]),0:np.array([200, 40, 70]),99:np.array([36, 90, 59])}
    HIGH_COLOR_EDIT = {1:np.array([360, 100, 100]),0:np.array([250, 100, 100]),99:np.array([42, 100, 100])}
    
    ##purple
    #LOW_COLOR_EDIT = {1:np.array([300, 59, 45]),0:np.array([200, 40, 70]),99:np.array([,,])}
    #HIGH_COLOR_EDIT = {1:np.array([360, 100, 100]),0:np.array([250, 100, 100]),99:np.array([,,)}
    

    # 抽出する色の塊のしきい値
    AREA_RATIO_THRESHOLD = 0.00003
    def __init__(self):
        self.pos = []
        ## DO NOT TOUCH HERE
        # h:1~179, s:1~255, v:1~255
        self.LOW_COLOR = {k:np.round(self.LOW_COLOR_EDIT[k]*self.hsv_coef) for k in self.LOW_COLOR_EDIT.keys()}
        self.HIGH_COLOR = {k:np.round(self.HIGH_COLOR_EDIT[k]*self.hsv_coef) for k in self.HIGH_COLOR_EDIT.keys()}
    

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
            print(self.pos[2])
            if connecting_state == 0:
                if self.pos[2] > 7500:   #2000 datta yo
                    aprc_clear = True #これは目標に到達できたかのbool値
            else:
                #print(self.pos[2])
                if self.pos[2] > 12000:
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

