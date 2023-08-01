"""
Description:
This moduel combines several functions including classes which are used for detecting AR-marker.
"""

# Import liblaries
import numpy as np
import cv2
from cv2 import aruco
from typing import Union
import sys
import time
import datetime

arm_id = "1"

# Definitions
"""
Classes
"""
class Ar_cansat():
    """ Class for detect AR marker and position

    """
    ## must be changed by id
#     marker_length = 0.009 # [m]
    #marker_length = 0.02 # [m]
    id_set = [1,2,3,4,5,6,7,8,9,10]
    def __init__(self):
        #レンズの性質などの内部パラメータ(今回はすでに行っている)
        self.camera_matrix = np.load("mtx.npy")
        self.distortion_coeff = np.load("dist.npy")
        # マーカーの辞書選択
        self.dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)  #ARマーカーの生成に使用
        #aruco.customDictionary(nMakers(ID数),Markersize,baseDictionary(基本となるディクショナリ))で独自のディクショナリ作成も可能
        self.id_size = {1:0.00998,2:0.00998,3:0.00998,4:0.00998,5:0.00998,6:0.00998,7:0.025,8:0.025,9:0.01,10:0.01}
        self.debug_mode = False
        self.estimate_norm = 1
        self.aprc_AR = False
        
    def addSpace(self,img):
        self.debug_mode = True
        white=[255,255,255]
        
        height,width,channels=img.shape
        
        output_img = cv2.copyMakeBorder(img,0,0,0,300,cv2.BORDER_CONSTANT,value=white)
        return output_img
    
    def show_info(self,img, i, k, norm_tvec,tvec,rvec,camera_matrix,distortion_coeff,draw_pole_length, corners, ids):
        img = aruco.drawAxis(img,self.camera_matrix,self.distortion_coeff,rvec,tvec,draw_pole_length)
        cv2.putText(img,
                    text = f"id:{i} | norm:{norm_tvec*100:.3f} [cm]",
                    org = (640,20+k*70),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.5,
                    thickness = 1,
                    color=(0,0,0),
                    lineType=cv2.LINE_4)
        
        cv2.putText(img,
                    text = f"    x:{str(round(tvec[0]*100,2))} | y:{str(round(tvec[1]*100,2))} | z:{str(round(tvec[2]*100,2))}",
                    org = (640,40+k*70),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.5,
                    thickness = 1,
                    color=(0,0,0),
                    lineType=cv2.LINE_4)
        
        cv2.putText(img,
                    text = f"    roll:{str(round(rvec[0],2))} | pitch:{str(round(rvec[1],2))} | yaw:{str(round(rvec[2],2))}",
                    org = (640,60+k*70),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 0.5,
                    thickness = 1,
                    color=(0,0,0),
                    lineType=cv2.LINE_4)
        # 可視化
        detected_img = aruco.drawDetectedMarkers(img, corners, ids, (255,0,255))
        return detected_img
        
    def detect_marker(self, img):
        #使用するARマーカーのライブラリ、マーカーの大きさは不変であるため宣言しておく必要あり
        self.ar_info = {}
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, self.dictionary)
        #print(ids[:][0])
        
        if len(corners) > 0:
                # マーカーごとに処理
            info_loop = {str(ids[i][0]) : corners[i] for i in range(len(ids))}
            
            #for i, corner in enumerate(corners):
            if len(ids)>1:
                ids_list = np.sort(np.squeeze(ids))
            else:
                ids_list = ids[0]
            
            #print(ids_list)
            for k, i in enumerate(ids_list):
                if i in self.id_set:
                    # print("i:",type(i))
                    makersize = self.id_size[i]
                    rvec, tvec, _ = aruco.estimatePoseSingleMarkers(info_loop[str(i)], makersize, self.camera_matrix, self.distortion_coeff)  #マーカーごとに外部パラメータ(回転ベクトルと並進ベクトル)を算出
                    # 不要なaxisを除去
                    tvec = np.squeeze(tvec)
                    rvec = np.squeeze(rvec)
                    # calculate norm
                    self.norm_tvec = np.linalg.norm(tvec)
                    # 回転ベクトルからrodorigues(回転行列)へ変換
                    rvec_matrix = cv2.Rodrigues(rvec)
                    rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し
                    # 並進ベクトルの転置
                    transpose_tvec = tvec[np.newaxis, :].T
                    # 合成（通称外部パラメータと呼ばれる，回転行列と並進ベクトルを列方向に結合）
                    proj_matrix = np.hstack((rvec_matrix, transpose_tvec))
                    # オイラー角への変換
                    euler_angle = cv2.decomposeProjectionMatrix(proj_matrix)[6] # [deg]
                    #不要な部分除去
                    euler = np.squeeze(euler_angle)

                    #print("x : " + str(tvec[0]))
                    #print("y : " + str(tvec[1]))
                    #print("z : " + str(tvec[2]))
                    #print("roll : " + str(euler_angle[0]))
                    #print("pitch: " + str(euler_angle[1]))
                    #print("yaw  : " + str(euler_angle[2]))
                    #可視化
                    #draw_pole_length = self.marker_length
                    #img = aruco.drawAxis(img,self.camera_matrix,self.distortion_coeff,rvec,tvec,draw_pole_length)
                    
                    # show ar_info
                    if self.debug_mode:
                        img = self.show_info(img, i, k, self.norm_tvec,tvec,rvec,self.camera_matrix,self.distortion_coeff,draw_pole_length,corners,ids)
            
                    """
                    cv2.putText(img,
                                text = f"id:{i} | norm:{self.norm_tvec*100:.3f} [cm]",
                                org = (640,20+k*70),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale = 0.5,
                                thickness = 1,
                                color=(0,0,0),
                                lineType=cv2.LINE_4)
                    
                    cv2.putText(img,
                                text = f"    x:{str(round(tvec[0]*100,2))} | y:{str(round(tvec[1]*100,2))} | z:{str(round(tvec[2]*100,2))}",
                                org = (640,40+k*70),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale = 0.5,
                                thickness = 1,
                                color=(0,0,0),
                                lineType=cv2.LINE_4)
                    
                    cv2.putText(img,
                                text = f"    roll:{str(round(rvec[0],2))} | pitch:{str(round(rvec[1],2))} | yaw:{str(round(rvec[2],2))}",
                                org = (640,60+k*70),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale = 0.5,
                                thickness = 1,
                                color=(0,0,0),
                                lineType=cv2.LINE_4)"""
                                
                    #cv2.imshow('drawDetectedMarkers', img)
                    #cv2.waitKey(0)
                    #cv2.destroyAllWindows()
                    self.ar_info[str(i)] = {'x':tvec[0],'y':tvec[1],'z':tvec[2],'roll':euler[0],'pitch':euler[1],'yaw':euler[2],'norm':self.norm_tvec,'rvec':rvec}
                    # self.ar_info.append(info)
                    
            
            # cv2.imwrite("detected.jpg",detected_img)
            # cv2.imwrite("axises.jpg",img)
        else:
            # img, self.ar_info = img, False # False -> {}
            img, self.ar_info = img, {}

        return img, self.ar_info
    
    def AR_decide(self, ar_info, connecting_state):
        """
        ARマーカーが見えたらAR出力にするためのbool値とID別のノルムの計算
        """
        side:str
        norm:float
        if connecting_state == 0:
            if "2" in ar_info.keys():
                self.aprc_AR = True
                side = 'marker_R'
                norm = ar_info['2']['norm']
                target_id = '2'
            else: 
                side = 'None'
                norm = 0
                self.aprc_AR = False
                target_id = 100

        else:
            if "3" in ar_info.keys() or "4" in ar_info.keys():
                self.aprc_AR = True
                side = 'marker_R'
                if "3" in ar_info.keys():
                    norm = ar_info['3']['norm']
                    target_id = '3'
                else:
                    norm = ar_info['4']['norm']
                    target_id = '4'
            elif "5" in ar_info.keys() or "6" in ar_info.keys() or "7" in ar_info.keys():
                self.aprc_AR = True
                side = 'marker_L'
                if "5" in ar_info.keys():
                    norm = ar_info['5']['norm']
                    target_id = '5'
                elif "6" in ar_info.keys():
                    norm = ar_info['6']['norm']
                    target_id = '6'
                else:
                    norm = ar_info['7']['norm']
                    target_id = '7'
            else:
                norm = 0
                side = 'None'
                self.aprc_AR = False
                target_id = 100
        
        return {"AR":self.aprc_AR, "side":side, "id":target_id, "norm":norm}


class Target(Ar_cansat):
    def __init__(self):
        super().__init__()
        
    def facing(self,ar_info) -> bool:
        """
        Description:
            
        """
        pitch=ar_info[arm_id]["pitch"]
        self.face_tf = False
        if abs(pitch)<10.0:
#             print("FRONT OF MARKER!!!!!")
            self.face_tf = True
        return self.face_tf
    
    def theta(self,info):
        x=info[arm_id]['x']
        z=info[arm_id]['z']
        
        norm=np.linalg.norm([x,z])
        self.arg=np.arcsin(x/norm)
        #print(theta)
        return self.arg
        
    
    def get_result(self):
        
        if self.facing(self.ar_info) and abs(self.arg)<np.pi/20 and abs(self.norm_tvec-0.27)<0.02:
            print("GOAL!!!!!!!")
        else:
            print("______________________")
            
    def find_vec(self,ar_info:dict={"1":{"x":0, "y":3, "z":5} ,"2":{"x":1, "y":0, "z":7} ,"3":{"x":0, "y":0, "z":0}}) -> dict:
        v_1, v_2 = False,False
        v1check, v2check = False, False
        
    #     marker_1 = np.array([ar_info["1"]["x"],ar_info["1"]["y"],ar_info["1"]["z"]])
    #     marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
    #     marker_3 = np.array([ar_info["3"]["x"],ar_info["3"]["y"],ar_info["3"]["z"]])
    # 
    #     #print(marker_1)
    #     
    #     v_1, v1check = __targetting(marker_1,marker_2, "module")
    #     v_2, v2check = __targetting(marker_3,marker_2, "wiring")
        
        key_list=ar_info.keys()
    #     print(key_list)
        if "1" in key_list and "2" in key_list:
            marker_1 = np.array([ar_info["1"]["x"],ar_info["1"]["y"],ar_info["1"]["z"]])
            marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
            v_1, v1check = self.__targetting(marker_1,marker_2, "module")
            #print("1,2")
        if "3" in key_list and "2" in key_list:
            marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
            marker_3 = np.array([ar_info["3"]["x"],ar_info["3"]["y"],ar_info["3"]["z"]])
            v_2, v2check = self.__targetting(marker_3,marker_2, "wiring")
            #print("3,2")
        
        
        return {"module":[v_1, v1check], "wiring":[v_2, v2check]}

    def __targetting(self,marker_1:np.ndarray=np.zeros(3), marker_2:np.ndarray=np.zeros(3), object="module") -> Union[list, bool]:
        target_vec = marker_2 - marker_1
        target_norm = np.linalg.norm(target_vec)
        if target_norm < 0.1:
            t_or_f = True
        else:
            t_or_f = False
        return target_vec, t_or_f
        
        
    #print(__targetting(np.array([[1,2,3]]), np.array([[3,2,1]]), "module"))
    #print(find_vec())


"""
Functions
"""
# vec_calc
#idは1：電源モジュール，2：通信モジュール，3：配線と仮定
def find_vec(ar_info:dict={"1":{"x":0, "y":3, "z":5} ,"2":{"x":1, "y":0, "z":7} ,"3":{"x":0, "y":0, "z":0}}) -> dict:
    v_1, v_2 = False,False
    v1check, v2check = False, False
    
#     marker_1 = np.array([ar_info["1"]["x"],ar_info["1"]["y"],ar_info["1"]["z"]])
#     marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
#     marker_3 = np.array([ar_info["3"]["x"],ar_info["3"]["y"],ar_info["3"]["z"]])
# 
#     #print(marker_1)
#     
#     v_1, v1check = __targetting(marker_1,marker_2, "module")
#     v_2, v2check = __targetting(marker_3,marker_2, "wiring")
    
    key_list=ar_info.keys()
#     print(key_list)
    if "1" in key_list and "2" in key_list:
        marker_1 = np.array([ar_info["1"]["x"],ar_info["1"]["y"],ar_info["1"]["z"]])
        marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
        v_1, v1check = __targetting(marker_1,marker_2, "module")
        #print("1,2")
    if "3" in key_list and "2" in key_list:
        marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
        marker_3 = np.array([ar_info["3"]["x"],ar_info["3"]["y"],ar_info["3"]["z"]])
        v_2, v2check = __targetting(marker_3,marker_2, "wiring")
        #print("3,2")
    
    
    return {"module":[v_1, v1check], "wiring":[v_2, v2check]}

def __targetting(marker_1:np.ndarray=np.zeros(3), marker_2:np.ndarray=np.zeros(3), object="module") -> Union[list, bool]:
    target_vec = marker_2 - marker_1
    target_norm = np.linalg.norm(target_vec)
    if target_norm < 0.1:
        t_or_f = True
    else:
        t_or_f = False
    return target_vec, t_or_f
    
    
#print(__targetting(np.array([[1,2,3]]), np.array([[3,2,1]]), "module"))
#print(find_vec())
