import numpy as np
import cv2
import sys
import time


##change camera
def camera(cap):
    """
    引数0→写真
    引数1→動画
    """
    ret, img = cap.read()      
    cv2.imshow('cameratest', img)
    # if cv2.waitKey(10) & 0xFF == ord('q'):
    #     break

# writer.release()
# cap.release()
# cv2.destroyAllWindows()

# if __name__ == '__main__':
#     args = sys.argv
#     main(args[1])

camera()
