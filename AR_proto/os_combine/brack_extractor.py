import cv2
import numpy as np

def get_color_hsv(frame):
    R_LOW = np.array([0, 0, 0])
    #R_HIGH = np.array([10, 30, 30])
    R_HIGH = np.array([179, 255, 30])
    # hsv色空間に変換
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    
    # 緑色
    r_hsv_mask = cv2.inRange(hsv,R_LOW,R_HIGH)
    br = cv2.bitwise_not(r_hsv_mask)
    # cv2.imwrite("hsv_r1.png",br)
    # 画像のマスク（合成）
    r_contours = cv2.bitwise_and(frame, frame, mask = r_hsv_mask)
    # cv2.imwrite("brack.png",r_contours)
    return br
    
# image = cv2.imread("AR_proto\os_combine\\test.png")
# get_color_hsv(image)