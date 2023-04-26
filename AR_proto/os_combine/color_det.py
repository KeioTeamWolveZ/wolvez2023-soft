import cv2
import numpy as np

from picamera2 import Picamera2
from libcamera import controls

import cv2
import numpy as np
"""
カラー毎の閾値設定(RGB)
"""
# 赤の色範囲を定義する
r_low = np.array([0, 0, 128])  # 赤の最小値
r_high = np.array([50, 50, 255])  # 赤の最大値

# 緑の色範囲を定義する
g_low = np.array([0, 128, 0])  # 緑の最小値
g_high = np.array([50, 255, 50])  # 緑の最大値


# 青の色範囲を定義する
b_low = np.array([128, 0, 0])  # 青の最小値
b_high = np.array([255, 50, 50])  # 青の最大値

"""
カラーの検出(RGB) ※RGBで検出と要検討(きっとRGBのほうが電力消費が少ない)
- input : image
- outout : 認識した色
"""
def get_color_rgb(frame):
    # 高さ，幅，チャンネル数
    h, w, c = frame.shape

    # 色を抽出
    # 赤色
    r_hsv_mask = cv2.inRange(frame,r_low,r_high)
    # 緑色
    g_hsv_mask = cv2.inRange(frame,g_low,g_high)
    # 青色
    b_hsv_mask = cv2.inRange(frame,b_low,b_high)

    # 1 画像のマスク（合成）
    r_contours = cv2.bitwise_and(frame, frame, mask = r_hsv_mask)
    g_contours = cv2.bitwise_and(frame, frame, mask = g_hsv_mask)
    b_contours = cv2.bitwise_and(frame, frame, mask = b_hsv_mask)

    cv2.imwrite("rgb_r.png",r_contours)
    cv2.imwrite("rgb_g.png",g_contours)
    cv2.imwrite("rgb_b.png",b_contours)

    # 判定
    # 赤色
    if np.all(r_contours == 0) :
        r_get = 0
        r_max_area = 0
        r_x = 0
        r_y = 0
    else:
        r_get = 1
        # 輪郭抽出
        r_contours,hierarchy = cv2.findContours(r_hsv_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 面積を計算
        r_areas = np.array(list(map(cv2.contourArea,r_contours)))
        r_max_idx = np.argmax(r_areas)
        r_max_area = r_areas[r_max_idx]
        r_max_a = r_areas[r_max_idx]
        result = cv2.moments(r_contours[r_max_idx])
        r_x = int(result["m10"]/result["m00"])
        r_y = int(result["m01"]/result["m00"])
 
    # 緑色
    if np.all(g_contours == 0) :
        g_get = 0
        g_max_area = 0
        g_x = 0
        g_y = 0
    else:
        g_get = 1
        # 輪郭抽出
        g_contours,hierarchy = cv2.findContours(g_hsv_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 面積を計算
        g_areas = np.array(list(map(cv2.contourArea,g_contours)))
        g_max_idx = np.argmax(g_areas)
        g_max_area = g_areas[g_max_idx]
        g_max_a = g_areas[g_max_idx]
        result = cv2.moments(g_contours[g_max_idx])
        g_x = int(result["m10"]/result["m00"])
        g_y = int(result["m01"]/result["m00"])
        
    # 青色
    if np.all(b_contours == 0) :
        b_get = 0
        b_max_area = 0
        b_x = 0
        b_y = 0
    else:
        b_get = 1
        # 輪郭抽出
        b_contours,hierarchy = cv2.findContours(b_hsv_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 面積を計算
        b_areas = np.array(list(map(cv2.contourArea,b_contours)))
        b_max_idx = np.argmax(b_areas)
        b_max_area = b_areas[b_max_idx]
        b_max_a = b_areas[b_max_idx]
        result = cv2.moments(b_contours[b_max_idx])
        b_x = int(result["m10"]/result["m00"])
        b_y = int(result["m01"]/result["m00"])
    get_color = [[r_get, g_get, b_get],[r_max_area, g_max_area, b_max_area],[[r_x, r_y], [g_x, g_y], [b_x, b_y]]]  # [r,g,b] on = 1, off = 0 
    return get_color
    

"""
カラー毎の閾値設定(HSV)
- 0 <= h <= 179 (色相)OpenCVではmax=179なのでR:0(180),G:60,B:120となる
- 0 <= s <= 255 (彩度)黒や白の値が抽出されるときはこの閾値を大きくする
- 0 <= v <= 255 (明度)これが大きいと明るく，小さいと暗い
"""

# 赤色の範囲を定義する
R_LOW_1 = np.array([0, 50, 50])
R_HIGH_1 = np.array([10, 255, 255])
R_LOW_2 = np.array([170, 50, 50])
R_HIGH_2 = np.array([180, 255, 255])

#green
G_LOW = np.array([36, 25, 25])
G_HIGH = np.array([70, 255, 255])

#blue
B_LOW = np.array([100, 75, 75])
B_HIGH = np.array([140, 255, 255])

# 抽出する青色の塊のしきい値
#AREA_RATIO_THRESHOLD = 0.005

"""
カラーの検出(HSV) ※RGBで検出と要検討(きっとRGBのほうが電力消費が少ない)
- input : image
- outout : 認識した色
"""

def get_color_hsv(frame):
    # 高さ，幅，チャンネル数
    h, w, c = frame.shape

    # hsv色空間に変換
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    
    # 色を抽出
    # 赤色
    r_hsv_mask1 = cv2.inRange(hsv,R_LOW_1,R_HIGH_1)
    r_hsv_mask2 = cv2.inRange(hsv,R_LOW_2,R_HIGH_2)
    # ２つの領域を統合
    r_hsv_mask = r_hsv_mask1 | r_hsv_mask2
    # 緑色
    g_hsv_mask = cv2.inRange(hsv,G_LOW,G_HIGH)
    # 青色
    b_hsv_mask = cv2.inRange(hsv,B_LOW,B_HIGH)

    # 画像のマスク（合成）
    r_contours = cv2.bitwise_and(frame, frame, mask = r_hsv_mask)
    g_contours = cv2.bitwise_and(frame, frame, mask = g_hsv_mask)
    b_contours = cv2.bitwise_and(frame, frame, mask = b_hsv_mask)
    cv2.imwrite("hsv_r.png",r_contours)
    cv2.imwrite("hsv_g.png",g_contours)
    cv2.imwrite("hsv_b.png",b_contours)
    # 判定
    # 赤色
    if np.all(r_contours == 0) :
        r_get = 0
        r_max_area = 0
        r_x = 0
        r_y = 0
    else:
        r_get = 1
        # 輪郭抽出
        r_contours,hierarchy = cv2.findContours(r_hsv_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        #hsv_r_cont = cv2.drawContours(frame, r_contours, -1, (0, 255, 0), 2, cv2.LINE_AA)
        #cv2.imwrite("hsv_r.png",hsv_r_cont)
        # 面積を計算
        r_areas = np.array(list(map(cv2.contourArea,r_contours)))
        r_max_idx = np.argmax(r_areas)
        r_max_area = r_areas[r_max_idx]
        r_max_a = r_areas[r_max_idx]
        result = cv2.moments(r_contours[r_max_idx])
        r_x = int(result["m10"]/result["m00"])
        r_y = int(result["m01"]/result["m00"])
 
    # 緑色
    if np.all(g_contours == 0) :
        g_get = 0
        g_max_area = 0
        g_x = 0
        g_y = 0
    else:
        g_get = 1
        # 輪郭抽出
        g_contours,hierarchy = cv2.findContours(g_hsv_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 面積を計算
        g_areas = np.array(list(map(cv2.contourArea,g_contours)))
        g_max_idx = np.argmax(g_areas)
        g_max_area = g_areas[g_max_idx]
        g_max_a = g_areas[g_max_idx]
        result = cv2.moments(g_contours[g_max_idx])
        g_x = int(result["m10"]/result["m00"])
        g_y = int(result["m01"]/result["m00"])
        
    # 青色
    if np.all(b_contours == 0) :
        b_get = 0
        b_max_area = 0
        b_x = 0
        b_y = 0
    else:
        b_get = 1
        # 輪郭抽出
        b_contours,hierarchy = cv2.findContours(b_hsv_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        # 面積を計算
        b_areas = np.array(list(map(cv2.contourArea,b_contours)))
        b_max_idx = np.argmax(b_areas)
        b_max_area = b_areas[b_max_idx]
        b_max_a = b_areas[b_max_idx]
        result = cv2.moments(b_contours[b_max_idx])
        b_x = int(result["m10"]/result["m00"])
        b_y = int(result["m01"]/result["m00"])
    
    get_color = [[r_get, g_get, b_get],[r_max_area, g_max_area, b_max_area],[[r_x, r_y], [g_x, g_y], [b_x, b_y]]]  # [r,g,b] on = 1, off = 0 
    return get_color

"""
#img = cv2.imread("pose_test.jpg")
img_rgb = cv2.imread("test.png")
img_hsv = cv2.imread("test.png")

get1 = get_color_rgb(img_rgb)
get2 = get_color_hsv(img_hsv)
# 抽出した座標に丸を描く
cv2.circle(img_rgb,get1[2][0],10,(0,125,255),-1)
cv2.circle(img_rgb,get1[2][1],10,(255,0,125),-1)
cv2.circle(img_rgb,get1[2][2],10,(125,255,0),-1)
cv2.imwrite('rgb.png',img_rgb)
key = cv2.waitKey(0)
# 抽出した座標に丸を描く
cv2.circle(img_hsv,get2[2][0],10,(0,125,255),-1)
cv2.circle(img_hsv,get2[2][1],10,(255,0,125),-1)
cv2.circle(img_hsv,get2[2][2],10,(125,255,0),-1)
cv2.imwrite('hsv.png',img_hsv)
key = cv2.waitKey(0)
print("RGB:" + str(get1))
print("HSV:" + str(get2))
"""


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
    # img = rgba2rgb(img)
    img = img[:,:,:3]
    
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
    
if __name__ == "__main__":
    main()
