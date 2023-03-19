import numpy as np
import cv2
from cv2 import aruco
import sys
import time
import datetime

import ar_module

ar = ar_module.Ar_cansat()
while True:
    img = ar.capture(1)
    detected_img, ar_info = ar.detect_marker(img)
    ar.show(detected_img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break


# cap = cv2.VideoCapture(0)
# while True:
#     ret, img = cap.read()
#     cv2.imshow("video",img)
#     if cv2.waitKey(10) & 0xFF == ord('q'):
#         break