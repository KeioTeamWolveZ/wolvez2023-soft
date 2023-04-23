import glob
import cv2

def addSpace(img):
    white=[255,255,255]
    
    height,width,channels=img.shape
    
    output_img = cv2.copyMakeBorder(img,0,0,0,300,cv2.BORDER_CONSTANT,value=white)
    return output_img