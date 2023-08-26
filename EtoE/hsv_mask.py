import cv2
import glob
import numpy as np
import sys


argument = sys.argv

if  len(argument) > 1:
    read_dir = argument[1]
    print(read_dir)
    #fnames = glob.glob(f'/home/wolvez2023/wolvez2023-soft/EtoE/results/{read_dir}/imgs/*.jpg')
    fnames = glob.glob(f'results/{read_dir}/imgs/*.jpg')
else:
#    read_dir = glob.glob('/home/wolvez2023/wolvez2023-soft/EtoE/results/*/')
    read_dir = glob.glob('results/*/')
    read_dir = sorted(read_dir)
    fnames = glob.glob(f'{read_dir[-1]}/imgs/*.jpg')
    fnames = sorted(fnames, key=lambda x: int(x.split('/')[-1].split('-')[0]))
#print("read_dir",read_dir)
print(fnames)


#print(fnames)
#fnames = sorted(fnames, key=lambda x: int(x.split('-')[0]))
#print("fnames\n",fnames)

i = 0
try:
    while True:
        #print(i)
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

        window_width = 525
        window_height = 390

        # 画像を指定したサイズで表示
        result = cv2.resize(result, (window_width, window_height))
        image = cv2.resize(image, (window_width, window_height))
        
        concatenated = cv2.hconcat([image,result])


        
        
        cv2.imshow('Extracted Color', concatenated)
        cv2.waitKey()
        cv2.destroyAllWindows()

        i += 1
except KeyboardInterrupt:
    cv2.destroyAllWindows()
    sys.exit()
