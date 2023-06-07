import numpy as np

def AR_powerplanner(ar_info:dict={"1":{"x":0, "y":3, "z":5} ,"2":{"x":1, "y":0, "z":7} ,"3":{"x":0, "y":0, "z":0}}) -> dict:
    
    # 速度の設定
    STANDARD_POWER = 40
    POWER_RANGE = 10

    marker_1 = np.array([ar_info["1"]["x"],ar_info["1"]["y"],ar_info["1"]["z"]])
    marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
    vec, distance = __targetting(marker_1,marker_2, "arm_to_module")
    if distance > 0:
        if distance > 0.5:
            '''
            接近するまでは連続的に近づく(アームとモジュールが横並びするまで？)
            '''
            power_R = int(STANDARD_POWER + POWER_RANGE * distance)
            power_L = int(STANDARD_POWER - POWER_RANGE * distance)
        else:
            '''
            接近後なので回転したい
            '''
            power_R = int(POWER_RANGE * vec(0))
            power_L = int(-1 * POWER_RANGE * vec(0))
    else:
        '''
        distanceが負のときバックする？
        '''
        power_R = 0
        power_L = 0
    
    return power_R, power_L

def __targetting(marker_1:np.ndarray=np.zeros(3), marker_2:np.ndarray=np.zeros(3), object="module") -> Union[list, bool]:
    '''
    二つのベクトルの差分と閾値に対する評価を出力
    '''
    target_vec = marker_2 - marker_1
    distance = (vec(2)/abs(vec(2)))*(vec(0)^2 + vec(2)^2)^0.5 
    return target_vec, distance
    
#print(__targetting(np.array([[1,2,3]]), np.array([[3,2,1]]), "module"))
#print(find_vec())