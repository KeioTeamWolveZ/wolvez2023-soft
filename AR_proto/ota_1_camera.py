import numpy as np
import cv2
from cv2 import aruco

cap = cv2.VideoCapture('/Users/otako/wolvez/wolvez2023-soft/AR_proto/test.jpg')
ret, img = cap.read()
##cap = cv2.VideoCapture(0)   #PCのかめら
# マーカーサイズ
marker_length = 0.056 # [m]
# マーカーの辞書選択
dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)  #ARマーカーの生成に使用
#aruco.customDictionary(nMakers(ID数),Markersize,baseDictionary(基本となるディクショナリ))で独自のディクショナリ作成も可能

#レンズの性質などの内部パラメータ
camera_matrix = np.load("mtx.npy")
distortion_coeff = np.load("dist.npy")


def camera(gazou,ARmarker):
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gazou, ARmarker)
    # 可視化
    aruco.drawDetectedMarkers(gazou, corners, ids, (0,255,255))
    if len(corners) > 0:
            # マーカーごとに処理
        for i, corner in enumerate(corners):
            rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, marker_length, camera_matrix, distortion_coeff)  #マーカーごとに外部パラメータ(回転ベクトルと並進ベクトル)を算出
            # 不要なaxisを除去
            tvec = np.squeeze(tvec)
            rvec = np.squeeze(rvec)
            # 回転ベクトルからrodoriguesへ変換
            rvec_matrix = cv2.Rodrigues(rvec)
            rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し
            # 並進ベクトルの転置
            transpose_tvec = tvec[np.newaxis, :].T
            # 合成
            proj_matrix = np.hstack((rvec_matrix, transpose_tvec))
            # オイラー角への変換
            euler_angle = cv2.decomposeProjectionMatrix(proj_matrix)[6] # [deg]
    
            print("x : " + str(tvec[0]))
            print("y : " + str(tvec[1]))
            print("z : " + str(tvec[2]))
            print("roll : " + str(euler_angle[0]))
            print("pitch: " + str(euler_angle[1]))
            print("yaw  : " + str(euler_angle[2]))
            cv2.imshow('drawDetectedMarkers', gazou)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

x = camera(img, dictionary)