import numpy as np
import cv2
from cv2 import aruco


cap = cv2.VideoCapture('test.jpg')
ret, img = cap.read()         #読み込んで画像として定義
##cap = cv2.VideoCapture(0)   #PCのかめら
# マーカーサイズ
marker_length = 0.1 # [m]
# マーカーの辞書選択
dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)  #ARマーカーの生成に使用
#aruco.customDictionary(nMakers(ID数),Markersize,baseDictionary(基本となるディクショナリ))で独自のディクショナリ作成も可能

#レンズの性質などの内部パラメータ(今回はすでに行っている)
camera_matrix = np.load("mtx.npy")
distortion_coeff = np.load("dist.npy")


def camera(gazou):      #引数に画像
                        #使用するARマーカーのライブラリ、マーカーの大きさは不変であるため宣言しておく必要あり
    ar_info = []
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gazou, dictionary)
    # 可視化
    #aruco.drawDetectedMarkers(gazou, corners, ids, (255,0,255))
    if len(corners) > 0:
            # マーカーごとに処理
        for i, corner in enumerate(corners):
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, marker_length, camera_matrix, distortion_coeff)  #マーカーごとに外部パラメータ(回転ベクトルと並進ベクトル)を算出
            # 不要なaxisを除去
            tvec = np.squeeze(tvec)
            rvec = np.squeeze(rvec)
            # 回転ベクトルからrodorigues(回転行列)へ変換
            rvec_matrix = cv2.Rodrigues(rvec)
            rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し
            # 並進ベクトルの転置
            transpose_tvec = tvec[np.newaxis, :].T
            # 合成
            proj_matrix = np.hstack((rvec_matrix, transpose_tvec))
            # オイラー角への変換
            euler_angle = cv2.decomposeProjectionMatrix(proj_matrix)[6] # [deg]
            #不要な部分除去
            euler = np.squeeze(euler_angle)

            #print("x : " + str(tvec[0]))
            #print("y : " + str(tvec[1]))
            #print("z : " + str(tvec[2]))
            #print("roll : " + str(euler_angle[0]))
            #print("pitch: " + str(euler_angle[1]))
            #print("yaw  : " + str(euler_angle[2]))
            #可視化
            #cv2.imshow('drawDetectedMarkers', gazou)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()
            info = {'id':ids[i][0],'x':tvec[0],'y':tvec[1],'z':tvec[2],'roll':euler[0],'pitch':euler[1],'yaw':euler[2]}
            ar_info.append(info)
    return  ar_info  #idとそれに対するxyz座標のベクトルとそれぞれの回転の度合い(deg)が入ったリストを返す

print(camera(img))
