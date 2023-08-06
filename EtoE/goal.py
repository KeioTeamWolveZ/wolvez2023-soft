import numpy as np
import cv2
import matplotlib.pyplot as plt

# サンプル
#"10"は試験用
AR_info={'3': {'x': -0.09114616567451715, 'y': 0.002744899441449885, 'z': 0.28792481224443206, 'roll': 147.52030135072664, 'pitch': -25.483904387026094, 'yaw': -7.15703331563767, 'norm': 0.3020196276669807},
         '4': {'x': -0.04449822983187332, 'y': 0.03816098097571812, 'z': 0.24917629717173426, 'roll': -160.55307022966917, 'pitch': -7.330337708389204, 'yaw': -3.8734322766683698, 'norm': 0.25597886631402944},
         '5': {'x': -0.04449822983187332, 'y': 0.03816098097571812, 'z': 0.24917629717173426, 'roll': 0.0, 'pitch': -90.0, 'yaw': 0.0, 'norm': 0.25597886631402944},
         '10': {'x': 1, 'y': 1, 'z': 1, 'roll': 0.0, 'pitch': -180.0, 'yaw': 0.0, 'norm': 1.4}}


# 各マーカーに対するxg,yg,zg
marker_goal = {"3":[0.01,0.01,0.01],"4":[0.008,0.0,-0.006],"5":[-0.01,0,0],"6":[-0.008,0.01,-0.006],"10":[1,1,1]}
# 参照するマーカーの優先度順
marker_ref = ["10","5","3","6","4"]

def goal(ar_info):
    """
    arg : 
        ar_info = {'x':x,'y':y,'z':z,'roll':roll,'pitch':pitch,'yaw':yaw,'norm':norm}
    return:
        Xg,Yg,Zg : カメラ座標系におけるゴール座標
    """

    goals = {} 
    
    for n in ar_info.keys():
        x = ar_info[n]['x'] 
        y = ar_info[n]['y']
        z = ar_info[n]['z']
        roll = ar_info[n]['roll']
        pitch = ar_info[n]['pitch']
        yaw = ar_info[n]['yaw']
        bias = marker_goal[n] # マーカーからゴールまでのベクトル

        rvec = np.array([roll, pitch, yaw]) 
        rvec_matrix = cv2.Rodrigues(rvec) # rodorigues
        rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し

        g = np.dot(rvec_matrix,bias).reshape(-1, 1)+[[x],[y],[z]]

        goals[n] = g
    
    # 優先して参照する値を獲得
    print(goals)
    for ref in marker_ref:
        if ref in goals.keys():
            goal = goals[ref]
            break
    
    return goal


## 確認　X,Z平面で確認する
goal = goal(AR_info)
Xg = goal[0][0] # 取得したXg
Zg = goal[2][0] # 取得したZg
x = AR_info["10"]['x'] 
z = AR_info["10"]['z']

print(f"x={x}\nz={z}")
print(f"Xg={Xg}\nZg={Zg}")
plt.plot(0,0)
plt.plot(x,z,".") # ARマーカーの位置
plt.plot(Xg,Zg,"*") # ずらした後の位置
plt.axis('equal')
plt.show()