import numpy as np
import time

from arm import Arm
from power_planner import find_specific_color

#arm_output
arm = Arm(23)
arm.setup()

#color_define
LOW_COLOR = {0:np.array([[0, 64, 0],[150, 64, 0]]),1:np.array([100, 75, 75])}
HIGH_COLOR = {0:np.array([[30, 255, 255],[179, 255, 255]]),1:np.array([140, 255, 255])}

# 抽出する青色の塊のしきい値
AREA_RATIO_THRESHOLD = 0.0005 #tikai toki no module ni tyousei > ookiku te yoi

Module_Height = {0:700,1:500} 

def arm_grasping():
	for i in range(50,65):
		arm.move(i/10)
		time.sleep(0.2)
	time.sleep(1)
	arm.move(5.5)
	time.sleep(1)
	arm.stop()
	GPIO.cleanup()
	
def checking(frame,connecting_state):
	grasp_clear = False
	
	arm.move(8.5)
	time.sleep(1)
	arm.stop()
	GPIO.cleanup()
	
	pos = find_specific_color(
            frame,
            AREA_RATIO_THRESHOLD,
            LOW_COLOR,
            HIGH_COLOR,
            connecting_state
        )
    if pos is not None:
        detected = True
		if pos[1] > Module_Height[connecting_state]:
			grasp_clear = True
			print('hazihazihazi')
		else:
			arm.move(5.5)
			time.sleep(1)
			arm.stop()
			GPIO.cleanup()
	else:
		detected = False

return {"grasp_clear":grasp_clear,"Detected_tf":detected}
