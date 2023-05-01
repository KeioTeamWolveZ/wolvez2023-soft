from DubinsPlan import *
import numpy as np
import matplotlib.pyplot as plt

dubins=DubinsPath()
dubins.dubinspath(0.0,0.0,0.0,5.0,10.0,45.0,3.0)



AR_info={'1': {'x': -0.09114616567451715, 'y': 0.002744899441449885, 'z': 0.28792481224443206, 'roll': 147.52030135072664, 'pitch': -25.483904387026094, 'yaw': -7.15703331563767, 'norm': 0.3020196276669807},
         '2': {'x': -0.04449822983187332, 'y': 0.03816098097571812, 'z': 0.24917629717173426, 'roll': -160.55307022966917, 'pitch': -7.330337708389204, 'yaw': -3.8734322766683698, 'norm': 0.25597886631402944}}




def detect_target(info):
    l_arm = 0.1
    x1 = info["1"]["x"]
    y1 = info["1"]["z"]
    x2 = info["2"]["x"]
    y2 = info["2"]["z"]

    xc = (x1+x2)/2
    yc = (y1+y2)/2
    norm = np.sqrt((x1-x2)**2+(y1-y2)**2)
    xs = xc-l_arm*(y1-y2)/norm
    ys = yc+l_arm*(x1-x2)/norm

    yaws = np.rad2deg(np.arccos((y1-y2)/norm))
    dubins = DubinsPath()
    plan=dubins.dubinspath(0.0,0.0,0.0,xs,ys,yaws,0.03)
    

    return xs,ys,yaws,plan

xs,ys,yaws,plan = detect_target(AR_info)
x1 = AR_info["1"]["x"]
y1 = AR_info["1"]["z"]
x2 = AR_info["2"]["x"]
y2 = AR_info["2"]["z"]
print(xs,ys,plan)

fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111)

ax.plot(x1,y1,'.')
ax.plot(x2,y2,'.')
ax.plot(xs,ys,'*')
ax.plot(0,0,'s')
ax.set_xlim(-0.3,0.3)
ax.set_ylim(-0.3,0.3)

#plt.xlim(0,60)
#plt.ylim(0,60)
ax.set_aspect('equal', adjustable='box')

#dubins = DubinsPath()
#plan=dubins.dubinspath(0.0,0.0,0.0,xs,ys,yaws,10.0)
#print(plan)
plt.show()

