import motor
import time
import math
import constant as ct
import numpy as np
import matplotlib.pyplot as plt

# GPIO.setwarnings(False)
Motor1 = motor.motor(6,5,13)
Motor2 = motor.motor(20,16,12)


class DubinsPath():
    """
    経路計画を立てるためのクラス
    「どの向きにどれくらい進むか」が分かります。
    """
    def __init__(self):
        return
    
    def mod2pi(self, theta):
        return theta - 2.0 * math.pi * math.floor(theta / 2.0 / math.pi)

    def pi_2_pi(self,angle):
        while(angle >= math.pi):
            angle = angle - 2.0 * math.pi
        while(angle <= -math.pi):
            angle = angle + 2.0 * math.pi
        return angle

    def LSL(self, alpha, beta, d):
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)

        tmp0 = d + sa - sb

        mode = ["L", "S", "L"]
        p_squared = 2 + (d * d) - (2 * c_ab) + (2 * d * (sa - sb))
        if p_squared < 0:
            return None, None, None, mode
        tmp1 = math.atan2((cb - ca), tmp0)
        t = self.mod2pi(-alpha + tmp1)
        p = math.sqrt(p_squared)
        q = self.mod2pi(beta - tmp1)
        #  print(math.degrees(t), p, math.degrees(q))
        return t, p, q, mode

    def RSR(self, alpha, beta, d):
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)

        tmp0 = d - sa + sb
        mode = ["R", "S", "R"]
        p_squared = 2 + (d * d) - (2 * c_ab) + (2 * d * (sb - sa))
        if p_squared < 0:
            return None, None, None, mode
        tmp1 = math.atan2((ca - cb), tmp0)
        t = self.mod2pi(alpha - tmp1)
        p = math.sqrt(p_squared)
        q = self.mod2pi(-beta + tmp1)
        return t, p, q, mode

    def LSR(self, alpha, beta, d):
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)

        p_squared = -2 + (d * d) + (2 * c_ab) + (2 * d * (sa + sb))
        mode = ["L", "S", "R"]
        if p_squared < 0:
            return None, None, None, mode
        p = math.sqrt(p_squared)
        tmp2 = math.atan2((-ca - cb), (d + sa + sb)) - math.atan2(-2.0, p)
        t = self.mod2pi(-alpha + tmp2)
        q = self.mod2pi(-self.mod2pi(beta) + tmp2)
        return t, p, q, mode

    def RSL(self, alpha, beta, d):
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)

        p_squared = (d * d) - 2 + (2 * c_ab) - (2 * d * (sa + sb))
        mode = ["R", "S", "L"]
        if p_squared < 0:
            return None, None, None, mode
        p = math.sqrt(p_squared)
        tmp2 = math.atan2((ca + cb), (d - sa - sb)) - math.atan2(2.0, p)
        t = self.mod2pi(alpha - tmp2)
        q = self.mod2pi(beta - tmp2)
        return t, p, q, mode

    def RLR(self, alpha, beta, d):
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)

        mode = ["R", "L", "R"]
        tmp_rlr = (6.0 - d * d + 2.0 * c_ab + 2.0 * d * (sa - sb)) / 8.0
        if abs(tmp_rlr) > 1.0:
            return None, None, None, mode

        p = self.mod2pi(2 * math.pi - math.acos(tmp_rlr))
        t = self.mod2pi(alpha - math.atan2(ca - cb, d - sa + sb) + self.mod2pi(p / 2.0))
        q = self.mod2pi(alpha - beta - t + self.mod2pi(p))
        return t, p, q, mode
    
    def LRL(self, alpha, beta, d):
        sa = math.sin(alpha)
        sb = math.sin(beta)
        ca = math.cos(alpha)
        cb = math.cos(beta)
        c_ab = math.cos(alpha - beta)

        mode = ["L", "R", "L"]
        tmp_lrl = (6. - d * d + 2 * c_ab + 2 * d * (- sa + sb)) / 8.
        if abs(tmp_lrl) > 1:
            return None, None, None, mode
        p = self.mod2pi(2 * math.pi - math.acos(tmp_lrl))
        t = self.mod2pi(-alpha - math.atan2(ca - cb, d + sa - sb) + p / 2.)
        q = self.mod2pi(self.mod2pi(beta) - alpha - t + self.mod2pi(p))
        return t, p, q, mode

    def dubins_path_planning_from_origin(self, ex, ey, eyaw, c):
        # nomalize
        dx = ex
        dy = ey
        D = math.sqrt(dx ** 2.0 + dy ** 2.0)
        d = D / c
        #  print(dx, dy, D, d)

        theta = self.mod2pi(math.atan2(dy, dx))
        alpha = self.mod2pi(- theta)
        beta = self.mod2pi(eyaw - theta)
        #  print(theta, alpha, beta, d)

        planners = [self.LSL, self.RSR, self.LSR, self.RSL, self.RLR, self.LRL]

        bcost = float("inf")
        bt, bp, bq, bmode = None, None, None, None

        for planner in planners:
            t, p, q, mode = planner(alpha, beta, d)
            if t == None:
                #  print("".join(mode) + " cannot generate path")
                continue

            cost = (abs(t) + abs(p) + abs(q))
            if bcost > cost:
                bt, bp, bq, bmode = t, p, q, mode
                bcost = cost

        run_plan = [[bmode[0],bt],[bmode[1],bp],[bmode[2],bq]]
        px, py, pyaw = self.generate_course([bt, bp, bq], bmode, c)
        return px, py, pyaw, bmode, bcost, run_plan

    def dubins_path_planning(self, sx, sy, syaw, ex, ey, eyaw, c):
        """
        Dubins path plannner
        input:
            sx x position of start point [m]
            sy y position of start point [m]
            syaw yaw angle of start point [rad]
            ex x position of end point [m]
            ey y position of end point [m]
            eyaw yaw angle of end point [rad]
            c curvature [1/m]
        output:
            px
            py
            pyaw
            mode
        """

        ex = ex - sx
        ey = ey - sy

        lex = math.cos(syaw) * ex + math.sin(syaw) * ey
        ley = - math.sin(syaw) * ex + math.cos(syaw) * ey
        leyaw = eyaw - syaw

        lpx, lpy, lpyaw, mode, clen, plan = self.dubins_path_planning_from_origin(
            lex, ley, leyaw, c)

        px = [math.cos(-syaw) * x + math.sin(-syaw) *
            y + sx for x, y in zip(lpx, lpy)]
        py = [- math.sin(-syaw) * x + math.cos(-syaw) *
            y + sy for x, y in zip(lpx, lpy)]
        pyaw = [self.pi_2_pi(iyaw + syaw) for iyaw in lpyaw]
        return px, py, pyaw, mode, clen, plan

    def generate_course(self, length, mode, c):

        px = [0.0]
        py = [0.0]
        pyaw = [0.0]

        for m, l in zip(mode, length):
            pd = 0.0
            if m == "S":
                d = 1.0 / c
            else:  # turning couse
                d = math.radians(3.0)

            while pd < abs(l - d):
                #  print(pd, l)
                px.append(px[-1] + d * c * math.cos(pyaw[-1]))
                py.append(py[-1] + d * c * math.sin(pyaw[-1]))

                if m == "L":  # left turn
                    pyaw.append(pyaw[-1] + d)
                elif m == "S":  # Straight
                    pyaw.append(pyaw[-1])
                elif m == "R":  # right turn
                    pyaw.append(pyaw[-1] - d)
                pd += d
            else:
                d = l - pd
                px.append(px[-1] + d * c * math.cos(pyaw[-1]))
                py.append(py[-1] + d * c * math.sin(pyaw[-1]))

                if m == "L":  # left turn
                    pyaw.append(pyaw[-1] + d)
                elif m == "S":  # Straight
                    pyaw.append(pyaw[-1])
                elif m == "R":  # right turn
                    pyaw.append(pyaw[-1] - d)
                pd += d
        return px, py, pyaw

    def dubinspath(self, sx ,sy ,syaw, ex, ey, eyaw, c):
        """
        input
            sx x position of start point [m]
            sy y position of start point [m]
            syaw yaw angle of start point [rad]
            ex x position of end point [m]
            ey y position of end point [m]
            eyaw yaw angle of end point [rad]
            c curvature [1/m]
        output
            plan list with driving mode and length [["R",*.****],["S",*.****],["L",*.****]]
        """
        # print("Dubins path planner sample start!!")

        start_x = sx  # [m]
        start_y = sy  # [m]
        start_yaw = math.radians(syaw)  # [rad]

        end_x = ex  # [m]
        end_y = ey  # [m]
        end_yaw = math.radians(eyaw)  # [rad]

        curvature = c
        
        px, py, pyaw, mode, clen, plan = self.dubins_path_planning(start_x, start_y, start_yaw,
                                                    end_x, end_y, end_yaw, curvature)
        # print(plan)
        return plan
    
class DubinsRunner(DubinsPath):
    global Motor1, Motor2
    is_planning = False
    is_navigation = False
    is_running = False
    dubins_state = 0
    
    def __init__(self):
        super().__init__()
        self.thre_const = {"R":ct.const.R_THRE, "L":ct.const.L_THRE, "S":ct.const.S_THRE}
        self.start: int
        self.end: int
    
    def planner(self,info):
        self.info = info
        xs,ys,yaws,plan = self.detect_target(info)
        thresholds = self.get_thres(self.dubins_state)
        self.is_planning = False
        self.is_navigation = True
        return xs,ys,yaws,plan
    
    def navigator(self,plan):
        if not self.is_running:
            mr,ml = self.get_motor_vref(plan[self.dubins_state][0])
            self.__runner(mr,ml)
            self.start = time.time()
            self.is_running = True
        else:
            self.end = time.time()
            if self.end-self.start >= self.thresholds:
                self.__stopper()
                self.is_running = False
                self.dubins_state += 1
                if self.dubins_state <= 2:
                    self.get_thres(self.dubins_state)
                else:
                    self.is_navigation = False
    
    def __runner(self,mr,ml):
        Motor1.go(mr)
        Motor2.go(ml)
    
    def __stopper(self):
        Motor1.stop()
        Motor2.stop()

    def get_thres(self, dubins_state):
        self.thresholds = self.thre_const[self.plan[dubins_state][0]]*self.plan[dubins_state][1]
    
    def get_motor_vref(self,phase):
        if phase == "L":  # left turn
            #print("Turning Left")
            mr = 0
            ml = 70
        elif phase == "S":  # Straight
            #print("Srtaight down")
            mr = 70
            ml = 70
        elif phase == "R":  # right turn
            #print("Srtaight down")
            mr = 70
            ml = 70
        return mr,ml
    
    def detect_target(self,info):
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
        plan=self.dubinspath(0.0,0.0,0.0,xs,ys,yaws,0.03)
        # self.plot_dubinspath(x1,y1,x2,y2,xs,ys)
        return xs,ys,yaws,plan

    def plot_dubinspath(self,x1,y1,x2,y2,xs,ys):
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111)
        ax.plot(x1,y1,'.')
        ax.plot(x2,y2,'.')
        ax.plot(xs,ys,'*')
        ax.plot(0,0,'s')
        ax.set_xlim(-0.3,0.3)
        ax.set_ylim(-0.3,0.3)
        ax.set_aspect('equal', adjustable='box')
        plt.show()
