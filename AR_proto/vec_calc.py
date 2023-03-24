import numpy as np
from typing import Union

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
        print("1,2")
    if "3" in key_list and "2" in key_list:
        marker_2 = np.array([ar_info["2"]["x"],ar_info["2"]["y"],ar_info["2"]["z"]])
        marker_3 = np.array([ar_info["3"]["x"],ar_info["3"]["y"],ar_info["3"]["z"]])
        v_2, v2check = __targetting(marker_3,marker_2, "wiring")
        print("3,2")
    
    
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
