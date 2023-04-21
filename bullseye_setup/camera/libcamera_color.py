import cv2
import numpy as np

from picamera2 import Picamera2
from libcamera import controls

# 0 <= h <= 179 (色相)　OpenCVではmax=179なのでR:0(180),G:60,B:120となる
# 0 <= s <= 255 (彩度)　黒や白の値が抽出されるときはこの閾値を大きくする
# 0 <= v <= 255 (明度)　これが大きいと明るく，小さいと暗い
# ここでは青色を抽出するので120±20を閾値とした
LOW_COLOR = np.array([100, 75, 75])
HIGH_COLOR = np.array([140, 255, 255])

# 抽出する青色の塊のしきい値
AREA_RATIO_THRESHOLD = 0.005

"""
ラズパイカメラからの映像をrgbへ変更
"""
def rgba2rgb( rgba, background=(255,255,255) ):
    # reference(https://stackoverflow.com/questions/50331463/convert-rgba-to-rgb-in-python)
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba

    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros( (row, col, 3), dtype='float32' )
    r, g, b, a = rgba[:,:,0], rgba[:,:,1], rgba[:,:,2], rgba[:,:,3]

    a = np.asarray( a, dtype='float32' ) / 255.0

    R, G, B = background

    rgb[:,:,0] = r * a + (1.0 - a) * R
    rgb[:,:,1] = g * a + (1.0 - a) * G
    rgb[:,:,2] = b * a + (1.0 - a) * B

    return np.asarray( rgb, dtype='uint8' )

"""
指定した範囲の色の物体の座標を取得する関数
frame: 画像
AREA_RATIO_THRESHOLD: area_ratio未満の塊は無視する
LOW_COLOR: 抽出する色の下限(h,s,v)
HIGH_COLOR: 抽出する色の上限(h,s,v)
"""
def find_specific_color(frame,AREA_RATIO_THRESHOLD,LOW_COLOR,HIGH_COLOR):
    # 高さ，幅，チャンネル数
    h, w, c = frame.shape

    # hsv色空間に変換
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    
    # 色を抽出する
    ex_img = cv2.inRange(hsv,LOW_COLOR,HIGH_COLOR)

    # 輪郭抽出
    #_,contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours,hierarchy = cv2.findContours(ex_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    # 面積を計算
    areas = np.array(list(map(cv2.contourArea,contours)))

    if len(areas) == 0 or np.max(areas) / (h*w) < AREA_RATIO_THRESHOLD:
        # 見つからなかったらNoneを返す
        print("the area is too small")
        return None
    else:
        # 面積が最大の塊の重心を計算し返す
        max_idx = np.argmax(areas)
        max_area = areas[max_idx]
        max_a = areas[max_idx]
        result = cv2.moments(contours[max_idx])
        x = int(result["m10"]/result["m00"])
        y = int(result["m01"]/result["m00"])
        return (x,y,max_area)

"""
静止画
Picamera2 : NO!!!!!!
"""
"""
def main():
    from picamera2 import Picamera2

    picam2 = Picamera2()

    #image
    #picam2.still_configuration.size=(800,600)
    #picam2.configure("still")
    #img = picam2.start_and_capture_file("test.jpg")
    picam2.start()
    #Libcamera's setting to use AF mode 
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    img = picam2.capture_array()
    img = rgba2rgb(img)
    
    # 位置を抽出
    pos = find_specific_color(
        img,
        AREA_RATIO_THRESHOLD,
        LOW_COLOR,
        HIGH_COLOR
    )

    if pos is not None:
        cv2.circle(img,pos,10,(0,0,255),-1)
    
    cv2.imwrite("result.jpg",img)
"""
"""
動画
"""

def main():
    # webカメラを扱うオブジェクトを取得
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888'}))
    picam2.start()
    
    #Libcamera's setting to use AF mode 
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    #picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous,"AFSeed":controls.AfSpeedEnum.Fast})
    
    #Get data
    img = picam2.capture_array()
    img = rgba2rgb(img)
    
    height, width = img.shape[:2]
    print("幅: " + str(width))
    print("高さ: " + str(height))

    while True:
        
        img = picam2.capture_array()

        if img is False:
            print("cannot read image")
            continue

        # 位置を抽出
        pos = find_specific_color(
            img,
            AREA_RATIO_THRESHOLD,
            LOW_COLOR,
            HIGH_COLOR
        )

        if pos is not None:
            # 抽出した座標に丸を描く
            cv2.circle(img,pos[0:2],10,(0,0,255),-1)
            
            # 中心座標と画面の中央の比較 (x軸)
            res_x = ""
            if pos[0] > width/2:
                res_x = "->"
            elif pos[0] < width/2:
                res_x = "<-"
            else:
                res_x = "--"
                
            #距離の閾値
            r=7000
            #距離の調節
            res_r = ""
            if pos[2] > r:
                res_r = "下がる"
            elif pos[2] < r:
                res_r = "近づく"
            else:
                res_r = "止まる"
            print(res_x + "," + str(pos[2]) + "," + res_r)
        
        # 画面に表示する
        cv2.imshow('frame',img)

        # キーボード入力待ち
        key = cv2.waitKey(1) & 0xFF

        # qが押された場合は終了する
        if key == 27:
            break
        
    picam2.stop()
    cv2.destroyAllWindows()
    
main()
