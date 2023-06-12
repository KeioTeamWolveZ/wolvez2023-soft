import numpy as np

aprc_AR = False

def AR_powerplanner(ar_info:dict={"1":{"x":0, "y":3, "z":5} ,"2":{"x":1, "y":0, "z":7} ,"3":{"x":0, "y":0, "z":0}}) -> dict:
    
    # 速度の設定
    STANDARD_POWER = 30
    POWER_RANGE = 10

    marker_1 = np.array([ar_info["1"]["x"],ar_info["1"]["y"],ar_info["1"]["z"]])
    marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
    vec, distance = __targetting(marker_1,marker_2)
    if distance > -0.5:
        if distance > 0.5:
            '''
            接近するまでは連続的に近づく(アームとモジュールが横並びするまで？)
            '''
            power_R = int(STANDARD_POWER + POWER_RANGE * distance)
            power_L = int(STANDARD_POWER - POWER_RANGE * distance)

        else:
            '''
            接近後なので回転したい：要検討
            '''
            power_R = int(POWER_RANGE * vec(0))
            power_L = int(-1 * POWER_RANGE * vec(0))

    else:
        '''
        distanceが負のときバックする？
        '''
        power_R = int(-1*STANDARD_POWER - POWER_RANGE * distance)
        power_L = int(-1*STANDARD_POWER + POWER_RANGE * distance)
    
    return {"R":power_R,"L":power_L}

def __targetting(marker_1:np.ndarray=np.zeros(3), marker_2:np.ndarray=np.zeros(3)):
    '''
    二つのベクトルの差分と閾値に対する評価を出力
    '''
    target_vec = marker_2 - marker_1
    #print(target_vec)
    distance = (target_vec[2]/abs(target_vec[2]))*(target_vec[0]**2 + target_vec[2]**2)**0.5 
    return target_vec, distance

#print(AR_powerplanner())