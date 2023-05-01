from DubinsPlan import *
import numpy as np
import matplotlib.pyplot as plt

dubins=DubinsPath()
dubins.dubinspath(0.0,0.0,0.0,5.0,10.0,45.0,3.0)



AR_info={"1":{'x':20.0,'y':40.0,'z':30.0,'roll':0.2,'pitch':0.3,'yaw':0.0,'norm':40},
            "2":{'x':40.0,'y':40.0,'z':25.0,'roll':0.2,'pitch':0.3,'yaw':0.0,'norm':40}}

l_arm = 30


def detect_target(info):
    x1 = info["1"]["x"]
    y1 = info["1"]["y"]
    x2 = info["2"]["x"]
    y2 = info["2"]["y"]

    xc = (x1+x2)/2
    yc = (y1+y2)/2
    norm = np.sqrt((x1-x2)**2+(y1-y2)**2)
    xs = xc-l_arm*(y1-y2)/norm
    ys = yc+l_arm*(x1-x2)/norm

    yaws = -np.rad2deg(np.arcsin(np.abs(y1-y2)/norm))+90

    return x1,y1,x2,y2,xs,ys,yaws

x1,y1,x2,y2,xs,ys,yaws = detect_target(AR_info)

print(x1,y1,x2,y2,xs,ys,yaws)

fig = plt.figure()
ax = fig.add_subplot(111)

plt.plot(x1,y1,'.')
plt.plot(x2,y2,'.')
plt.plot(xs,ys,'*')

plt.xlim(0,60)
plt.ylim(0,60)
ax.set_aspect('equal', adjustable='box')

dubins = DubinsPath()
plan=dubins.dubinspath(0.0,0.0,0.0,xs,ys,yaws,10.0)
print(plan)
plt.show()

