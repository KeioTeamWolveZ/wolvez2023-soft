import numpy as np
import time
import cv2
import RPi.GPIO as GPIO
from arm import Arm
from power_planner import find_specific_color

#arm_output
arm = Arm(23)
arm.setup()

#color_define
LOW_COLOR = {0:np.array([150, 64, 0]),1:np.array([100, 75, 75])}
HIGH_COLOR = {0:np.array([179, 255, 255]),1:np.array([140, 255, 255])}
# LOW_COLOR = {0:np.array([[0, 64, 0],[150, 64, 0]]),1:np.array([100, 75, 75])}
# HIGH_COLOR = {0:np.array([[30, 255, 255],[179, 255, 255]]),1:np.array([140, 255, 255])}

# 抽出する青色の塊のしきい値
AREA_RATIO_THRESHOLD = 0.0005 #tikai toki no module ni tyousei > ookiku te yoi

Module_Height = {0:500,1:700} 

def arm_grasping():
	# try:
		# arm.setup()
	# except:
		# pass
	arm.move(5.2)
	time.sleep(1)
	for i in range(52,70):
		arm.move(i/10)
		time.sleep(0.1)
	time.sleep(1)
	
	
	# import time
	# arm = Arm(23)
	# arm.setup()
	# #arm.up()
	# for i in range(55,80):
		# arm.move(i/10)
		# time.sleep(0.1)
	# time.sleep(1)
	# arm.down()
	# time.sleep(1)
	# arm.stop()
	# GPIO.cleanup()
	
def checking(frame,connecting_state):
	grasp_clear = False
	
	# try:
		# arm.setup()
	# except:
		# pass
	arm.move(8.3)
	time.sleep(1.0)
	
	pos = find_specific_color(frame,AREA_RATIO_THRESHOLD,LOW_COLOR,HIGH_COLOR,connecting_state)
	if pos is not None:
		print("pos:",pos[1],"\nTHRESHOLD:",Module_Height[connecting_state])
		detected = True
		if pos[1] < Module_Height[connecting_state]:
			grasp_clear = True
			arm.move(7.5)
			time.sleep(2.0)
			# arm.stop()
			print('===========\nGRASPED\n===========')
		else:
			arm.move(5.5)
			time.sleep(1)
			# arm.stop()
			print('===========\nFAILED\n===========')
	else:
		detected = False
		print('===========\nNO LOOK\n===========')

	return {"grasp_clear":grasp_clear,"Detected_tf":detected}
#arm_grasping()
