import numpy as np
import cv2
from cv2 import aruco
import sys
import time


def main(args):
    """
    引数0→写真
    引数1→動画
    """
    cap = cv2.VideoCapture(0)
    if args == "0":
        ret,img = cap.read()
        cv2.imwrite('test.jpg', img)
        print(ret)
    else:
#         now_time = time.time()
#         frame_rate = cap.get(cv2.CAP_PROP_FPS)
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         size = (width,height)
#         fmt = cv2.VideoWriter_fourcc("m","p","4","v")
#         writer = cv2.VideoWriter("./result/"+str(now_time)+".mp4",fmt,frame_rate,size)
        while True:
            ret, img = cap.read()
            
            edges = cv2.Canny(img,100,200)
            for i in range(img.shape[0]):
                for j in range(img.shape[1]):
                    print(img[i][j]+10)
#             writer.write(img)
#             cv2.imshow('cameratest', edges)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        
        writer.release()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    args = sys.argv
    main(args[1])
