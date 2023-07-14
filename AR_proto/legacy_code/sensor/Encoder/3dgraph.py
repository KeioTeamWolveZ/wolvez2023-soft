# -*- coding: utf-8 -*-
# 3D plot

#最初にいろいろとインストール必要があるのでいかに記す
#pip3 install --upgrade pip
#sudo pip3 install matplotlib
#pip3 install numpy --upgrade
#sudo apt-get install python3-gi-cairo
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
def pdf(xc,yc,r):
    w=3
    return 0.5*np.exp(-1*((w*X-xc)**2+(w*Y-yc)**2)/(2*r**2))*((w*X-xc)**2+(w*Y-yc)**2)/(2*math.pi*r**2)

# x, y成分のデータの作成
x = np.arange(-30, 31, 1)
y = np.arange(-30, 31, 1)
X, Y = np.meshgrid(x, y)
Z1=list()
Z1.append(pdf(0,3,5))
Z1.append(pdf(0,17,13))
Z1.append(pdf(9,0,12))
Z1.append(pdf(30,0,34))
Z1.append(pdf(20,0,16))

Z=sum(Z1)


Zc=np.unravel_index(np.argmax(Z), Z.shape)
#print(Zc[1],Zc[0])

fig = plt.figure()
ax = fig.add_subplot(111,projection="3d")
#ax = Axes3D(fig)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
surf=ax.plot_surface(X, Y, Z, cmap=plt.cm.jet,linewidth=0, antialiased=False)
ax.scatter(x[Zc[1]], y[Zc[0]], np.max(Z),s = 40,c='k',)

print(x[Zc[1]], y[Zc[0]])

# z軸の設定
ax.set_xlim(-30.01, 30.01)
ax.set_ylim(-30.01, 30.01)
ax.set_zlim(0.0, 0.5)
ax.view_init(30, 30)
fig.colorbar(surf, shrink=0.5, aspect=5)
#fig.savefig(str(111) + ".pdf")
plt.show()
