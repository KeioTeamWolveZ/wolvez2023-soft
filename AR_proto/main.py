import numpy as np
import cv2
from cv2 import aruco
import sys
import time
import datetime

import ar_module

save_video = False


ar = ar_module.Ar_cansat()

if save_video : ar.setup_video()

while True:
    img = ar.capture(1)
    img = ar.addSpace(img)
    detected_img, ar_info = ar.detect_marker(img)
    ar.show(detected_img)

    if save_video : ar.write_video(detected_img)

    # time.sleep(0.1)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

if save_video : ar.video.release()
ar.cap.release()
cv2.destroyAllWindows()