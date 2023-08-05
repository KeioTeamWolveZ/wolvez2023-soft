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
        self.marker_goal = {"2":[0.0,0.0,0.01],"3":[0,0.003,0.038],"4":[0,0.042,-0.005],"5":[0,0.042,-0.005],"6":[0,0.042,-0.005],"7":[0,0.042,-0.005],"10":[1,1,1],"68":[0,0,-0.06]}
        # 参照するマーカーの優先度順
        self.marker_ref = ["10","5","3","6","4"]

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
        #rvec_norm = np.linalg.norm(rvec)
        rvec_matrix = cv2.Rodrigues(rvec)
        rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し
        g = np.dot((rvec_matrix),vec).reshape(-1, 1)
        return g

    def goalvec_maker(self,ar_info,goal_point,connecting_state,id):
        self.connecting_state = connecting_state
        if connecting_state == 0:
            if self.arm_id in ar_info.keys():
                marker_1 = np.array([ar_info[self.arm_id]["x"],ar_info[self.arm_id]["y"],ar_info[self.arm_id]["z"]])
            else:
                marker_1 = np.array([0.0353238,0.00329190,0.15313373])
        else:
            marker_1 = np.array([0.003606,-0.015277,0.138732])
        vec, distance = self.__targetting(marker_1,goal_point)
        #print(f"vec:{vec[2]}")
        vec[2] = self.calc_t_distance(id,ar_info, vec, distance)
        goal_area = {"x":[-0.004,0.004],"z":[-0.004,0.004]}
        print(f"distance:{distance},vec:{vec}")

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
        if id == "2" or id == "3" or id == "68": # 68は裏面のマーカー、青モジュールに追加するマーカーも必要
            y_m = self.rot_vec(ar_info[id]['rvec'],[0,0,1])
        else:
            y_m = self.rot_vec(ar_info[id]['rvec'],[0,1,0])
        vec_normalize = vec.reshape(3,1)/np.linalg.norm(vec[1:3])
        #print(vec_normalize)
        cos_argment = np.dot(y_m[1:3].T,vec_normalize[1:3])
        #print(cos_argment)
        ultraman = distance*np.sqrt(1-cos_argment**2)
        #ultraman = distance*sin(arccos(y_m[1:3].T/vec_normalize[1:3]))
        return ultraman[0][0]
        
    def rotation_matrix(self, axis, theta):
        """
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.
        """
        axis = np.asarray(axis)
        axis = axis / np.sqrt(np.dot(axis, axis))
        a = np.cos(theta / 2.0)
        b, c, d = -axis * np.sin(theta / 2.0)
        aa, bb, cc, dd = a * a, b * b, c * c, d * d
        bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
        return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                         [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                         [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


    def __targetting(self,marker_1:np.ndarray=np.zeros(3), marker_2:np.ndarray=np.zeros(3)):
        '''
        二つのベクトルの差分と閾値に対する評価を出力
        '''
        target_vec = marker_2 - marker_1
        target_vec = target_vec[0]
        # print(np.linalg.norm(target_vec))
        #distance = (self.target_vec[2]/abs(target_vec[2]))*((target_vec[1]**2 + target_vec[2]**2)**0.5)
        distance = np.sign(target_vec[2])*np.linalg.norm(target_vec[1:3])
        return target_vec, distance
    


### module nomi kara sansyutu
# def AR_powerplanner_single(ar_info:dict={"1":{"x":0, "y":3, "z":5} ,"2":{"x":1, "y":0, "z":7} ,"3":{"x":0, "y":0, "z":0}}) -> dict:
    
    # # 速度の設定
    # STANDARD_POWER = 60
    # POWER_RANGE = 10
    # aprc_state = False

    # marker_1_kasou = np.array([0.069,0.028,0.144]) ### arm wo suihei ni sita toki no daitai no iti
    # marker_3 = np.array([ar_info["3"]["x"],ar_info["3"]["y"],ar_info["3"]["z"]])
    # vec, distance = __targetting(marker_1_kasou,marker_3)
    # #print(distance)
    # print(f"distance:{distance}")
    # if distance > -0.02:
        # if distance > 0.15:
            # '''
            # 接近するまでは連続的に近づく(アームとモジュールが横並びするまで？)
            # '''
            # #print(f"distance:{distance}")
            # #print(f"vec:{vec[0]}")
            # if vec[0] < 0.07:
                # power_R = int(STANDARD_POWER )
                # power_L = int(0)
            # else:
                # power_R = int(0)
                # power_L = int(STANDARD_POWER )
        # elif distance > 0.02:
            # if vec[0] < 0.01:
                # power_R = int(STANDARD_POWER-POWER_RANGE )
                # power_L = int(0)
            # else:
                # power_R = int(0)
                # power_L = int(STANDARD_POWER-POWER_RANGE )
        # else:
            # '''
            # 接近後なのでアーム動かしたい：要検討
            # '''
            # # print("finish")
            # power_R = 0
            # power_L = 0
            # aprc_state = True

    # else:
        # '''
        # distanceが負のときバックする？iranaikamo
        # '''
        # print("distance<0")
        # power_R = int(-1*STANDARD_POWER)
        # power_L = int(-1*STANDARD_POWER)
    
    # return {"R":power_R,"L":power_L,"aprc_state":aprc_state}
