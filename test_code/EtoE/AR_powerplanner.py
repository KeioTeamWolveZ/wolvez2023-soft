import numpy as np
arm_id = "1"

def AR_powerplanner(ar_info,AR_checker,connecting_state):
    
    # 速度の設定
    STANDARD_POWER = 90
    POWER_RANGE = 10
    aprc_state = False
    target_id = AR_checker["id"]
    if connecting_state == 0:
        marker_1 = np.array([ar_info[arm_id]["x"],ar_info[arm_id]["y"],ar_info[arm_id]["z"]])
        #marker_1 = np.array([0.0025,0.008755,0.1745])
        goal_area = {"L":[-0.035,-0.025],"R":[-0.005,0.005],"z":[0.01,0.03]}
    else:
        marker_1 = np.array([0.0025,0.008755,0.1745])
        goal_area = {"L":[-0.056,-0.046],"R":[0.019,0.029],"z":[-0.01,0.01]}
    marker_target = np.array([ar_info[target_id]["x"],ar_info[target_id]["y"],ar_info[target_id]["z"]])
    vec, distance = __targetting(marker_1,marker_target)
    #print(distance,vec[0])
    print(f"distance:{distance},vec:{vec}")
    threshold = {"marker_R":[0.07,0.02],"marker_L":[-0.07,0.02],} # 使ってない
    # if vec[0] > goal_area[0] and vec[0] < goal_area[1] and distance > goal_area[2] and distance < goal_area[3]:
        # '''
        # 接近後なのでアーム動かしたい：要検討
        # '''
        # print("finish")
        # power_R = 0
        # power_L = 0
        # aprc_state = True
    # elif distance < goal_area[2]:
        # '''
        # distanceが負のときバックする？iranaikamo
        # '''
        # print("distance<0")
        # power_R = int(-1*STANDARD_POWER+POWER_RANGE)
        # power_L = int(-1*STANDARD_POWER+POWER_RANGE-5)
    # elif distance > goal_area[3]:
        # '''
        # hutuu ni tikaduku
        # '''
        # # if vec[2] > 0.15:
            # # '''
            # # 接近する(アームとモジュールが横並びするまで？)
            # # '''
            # # if AR_checker["side"] == "marker_R":
            # # #print(f"distance:{distance}")
            # # #print(f"vec:{vec[0]}")
                # # if vec[0] < 0.03:
                    # # power_R = int(STANDARD_POWER )
                    # # power_L = int(0)
                # # else:
                    # # power_R = int(0)
                    # # power_L = int(STANDARD_POWER )
            # # else:
                # # if vec[0] > -0.03:
                    # # power_R = int(0)
                    # # power_L = int(STANDARD_POWER+5 )
                # # else:
                    # # power_R = int(STANDARD_POWER )
                    # # power_L = int(0)
        # # else:
        # if AR_checker["side"] == "marker_R":
            # if vec[0] < goal_area[1]:
                # power_R = int(STANDARD_POWER - POWER_RANGE )
                # power_L = int(0)
            # else:
                # power_R = int(0)
                # power_L = int(STANDARD_POWER - POWER_RANGE+5 )
        # else:
            # if vec[0] > goal_area[0]:
                # power_R = int(0)
                # power_L = int(STANDARD_POWER - POWER_RANGE+5 )
            # else:
                # power_R = int(STANDARD_POWER - POWER_RANGE )
                # power_L = int(0)
    # else:
        # '''
        # tikai kedo yokohaba ari : sonoba senkai 
        # '''
        # print("senkai")
        # power_R = int(vec[0]/abs(vec[0])*(STANDARD_POWER - POWER_RANGE + POWER_RANGE * vec[0]/10)) ### +- ga umareru youni
        # power_L = -power_R -5
    if vec[2] > goal_area["z"][0]:
        if vec[2] > goal_area["z"][1]:
            '''
            tooi toki no yatu ha kesita
            '''
            if AR_checker["side"] == "marker_R":
                if vec[0] > goal_area["R"][0] and vec[0] < goal_area["R"][1]:
                    power_R = int(STANDARD_POWER - POWER_RANGE)
                    power_L = int(STANDARD_POWER - POWER_RANGE+5)
                else:
                    if vec[0] < goal_area["R"][0]:
                        power_R = int(STANDARD_POWER - POWER_RANGE )
                        power_L = int(0)
                    else:
                        power_R = int(0)
                        power_L = int(STANDARD_POWER - POWER_RANGE)
            elif AR_checker["side"] == "marker_L":
                if vec[0] > goal_area["L"][0] and vec[0] < goal_area["L"][1]:
                    power_R = int(STANDARD_POWER - POWER_RANGE)
                    power_L = int(STANDARD_POWER - POWER_RANGE+5)
                else:
                    if vec[0] > goal_area["L"][1]:
                        power_R = int(0)
                        power_L = int(STANDARD_POWER - POWER_RANGE)
                    else:
                        power_R = int(STANDARD_POWER - POWER_RANGE )
                        power_L = int(0)

        else:
            # When z is satisfying the thresholds, cansat changes just orientation
            motor_ouput = STANDARD_POWER - POWER_RANGE
            if AR_checker["side"] == "marker_R":
                if vec[0] > goal_area["R"][0] and vec[0] < goal_area["R"][1]:
                    print("finish")
                    power_R = 0
                    power_L = 0
                    aprc_state = True
                else:
                    if vec[0] < goal_area["R"][0]:
                        power_R = int(motor_ouput)
                        power_L = int(-motor_ouput)
                    else:
                        power_R = int(-motor_ouput)
                        power_L = int(motor_ouput)
            elif AR_checker["side"] == "marker_L":
                if vec[0] > goal_area["L"][0] and vec[0] < goal_area["L"][1]:
                    print("finish")
                    power_R = 0
                    power_L = 0
                    aprc_state = True
                else:
                    if vec[0] > goal_area["L"][1]:
                        power_R = int(-motor_ouput)
                        power_L = int(motor_ouput+7)
                    else:
                        power_R = int(motor_ouput)
                        power_L = int(-motor_ouput -7)
            '''
            接近後なのでアーム動かしたい：要検討
            '''

    else:
        '''
        distanceが負のときバックする？iranaikamo
        '''
        print("distance<0")
        power_R = int(-1*STANDARD_POWER)
        power_L = int(-1*STANDARD_POWER)
    
    return {"R":power_R,"L":power_L,"aprc_state":aprc_state}


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

def __targetting(marker_1:np.ndarray=np.zeros(3), marker_2:np.ndarray=np.zeros(3)):
    '''
    二つのベクトルの差分と閾値に対する評価を出力
    '''
    target_vec = marker_2 - marker_1
    #print(target_vec)
    distance = (target_vec[2]/abs(target_vec[2]))*((target_vec[1]**2 + target_vec[2]**2)**0.5)
    return target_vec, distance

#print(AR_powerplanner())
