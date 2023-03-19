import matplotlib.pyplot as plt
from tqdm import tqdm
XYZ=[[1,2,1]]

def plot_all_frames(elev=90, azim=270):
    frames = []

    for t in tqdm(range(len(XYZ))):
        fig = plt.figure(figsize=(4,3))
        ax = Axes3D(fig)
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_zlim(-2, 2)
        ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")

        x, y, z = XYZ[t]
        ux, vx, wx = V_x[t]
        uy, vy, wy = V_y[t]
        uz, vz, wz = V_z[t]

        # draw marker
        ax.scatter(0, 0, 0, color="k")
        ax.quiver(0, 0, 0, 1, 0, 0, length=1, color="r")
        ax.quiver(0, 0, 0, 0, 1, 0, length=1, color="g")
        ax.quiver(0, 0, 0, 0, 0, 1, length=1, color="b")
        ax.plot([-1,1,1,-1,-1], [-1,-1,1,1,-1], [0,0,0,0,0], color="k", linestyle=":")

        # draw camera
        ax.quiver(x, y, z, ux, vx, wx, length=0.5, color="r")
        ax.quiver(x, y, z, uy, vy, wy, length=0.5, color="g")
        ax.quiver(x, y, z, uz, vz, wz, length=0.5, color="b")

        # save for animation
        fig.canvas.draw()
        frames.append(np.array(fig.canvas.renderer.buffer_rgba()))
        plt.close()
plot_all_frames()