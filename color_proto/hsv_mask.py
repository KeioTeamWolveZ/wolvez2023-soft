import cv2
import glob
import numpy as np

print(glob.glob('2023-08-12_21-34-50/imgs/*.jpg'))
fnames = glob.glob('2023-08-12_21-34-50/imgs/*.jpg')
i = 1
while True:
    print(i)
    fname = fnames[i]
    print(fname)
    image = cv2.imread(fname)  # 画像ファイル名を適切に変更
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    LOW_COLOR_EDIT = {1:np.array([300, 59, 45]),0:np.array([200, 40, 70]),99:np.array([36, 90, 59])}
    HIGH_COLOR_EDIT = {1:np.array([360, 100, 100]),0:np.array([250, 100, 100]),99:np.array([42, 100, 100])}

    hsv_coef = np.array([1/2, 2.55, 2.55])

    LOW_COLOR = {k:np.round(LOW_COLOR_EDIT[k]*hsv_coef) for k in LOW_COLOR_EDIT.keys()}
    HIGH_COLOR = {k:np.round(HIGH_COLOR_EDIT[k]*hsv_coef) for k in HIGH_COLOR_EDIT.keys()}
        

    lower_range = np.array(LOW_COLOR[0])  # 下限のHSV値
    upper_range = np.array(HIGH_COLOR[0])  # 上限のHSV値


    mask = cv2.inRange(hsv_image, lower_range, upper_range)

    result = cv2.bitwise_and(image, image, mask=mask)

    window_width = 800
    window_height = 600

    # 画像を指定したサイズで表示
    result = cv2.resize(result, (window_width, window_height))


    
    
    cv2.imshow('Extracted Color', result)
    cv2.waitKey()
    cv2.destroyAllWindows()

    i += 1
