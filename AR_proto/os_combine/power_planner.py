"""
power_plannerに1フレーム与えると以下の形で出力の指令を返します。
{"R":power_R,"L":power_L}
それぞれ基準となる出力(STANDARD_POWER)に対して定義する出力範囲(±POWER_RANGE)で変動します。
速度と抽出する色の設定をしてください。
"""

import cv2
import numpy as np

# 速度の設定
STANDARD_POWER = 40
POWER_RANGE = 10


# 色の設定
# 0 <= h <= 179 (色相)　OpenCVではmax=179なのでR:0(180),G:60,B:120となる
# 0 <= s <= 255 (彩度)　黒や白の値が抽出されるときはこの閾値を大きくする
# 0 <= v <= 255 (明度)　これが大きいと明るく，小さいと暗い
# ここでは青色を抽出するので120±20を閾値とした
LOW_COLOR = np.array([100, 75, 75])
HIGH_COLOR = np.array([140, 255, 255])

# 抽出する青色の塊のしきい値
AREA_RATIO_THRESHOLD = 0.005

"""
指定した範囲の色の物体の座標を取得する関数
frame: 画像
AREA_RATIO_THRESHOLD: area_ratio未満の塊は無視する
LOW_COLOR: 抽出する色の下限(h,s,v)
HIGH_COLOR: 抽出する色の上限(h,s,v)
"""
def find_specific_color(frame,AREA_RATIO_THRESHOLD,LOW_COLOR,HIGH_COLOR):
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


def power_calculation(pos,h,w):
    
    xn = 2*(pos[0]-w/2) / w
    power_R = int(STANDARD_POWER - POWER_RANGE * xn)
    power_L = int(STANDARD_POWER + POWER_RANGE * xn)
    
    return power_R,power_L

"""
def power_calculation(pos,h,w):
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

def power_planner(frame):
    height, width = frame.shape[:2]

    aprc_clear = False #これは目標に到達できたかのbool値

    pos = find_specific_color(
            frame,
            AREA_RATIO_THRESHOLD,
            LOW_COLOR,
            HIGH_COLOR
        )
    
    if pos is not None:
        power_R, power_L = power_calculation(pos,height,width)
        detected = True
        if pos[2] > 7000:
            aprc_clear = True #これは目標に到達できたかのbool値
        
    else:
        power_R, power_L = 0,0
        detected = False
    return {"R":power_R,"L":power_L,"Clear":aprc_clear,"Detected_tf":detected}
