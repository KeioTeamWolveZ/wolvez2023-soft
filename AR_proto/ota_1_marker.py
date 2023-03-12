
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
            # 不要なaxisを除去(2次元配列を1次元にする)
            tvec = np.squeeze(tvec)     #並進ベクトル(重ね合わせれば座標？)
            rvec = np.squeeze(rvec)     #回転ベクトル
            # 回転ベクトルからrodoriguesへ変換
            rvec_matrix = cv2.Rodrigues(rvec)   #ロドリゲスは回転行列への変換
            rvec_matrix = rvec_matrix[0] # rodoriguesから抜き出し
            # 回転ベクトルの転置
            rotation_T = np.transpose(rvec_matrix)
            #並進ベクトルを反転
            trans_inv = np.multiply(-1,tvec)
            #カメラ位置の算出
            camera_position = np.matmul(rotation_T, trans_inv)
            # オイラー角への変換
            x_d = rvec_matrix[:, 0]
            y_d = rvec_matrix[:, 1]
            z_d = rvec_matrix[:, 2]
            pitch = np.arcsin(-1 * y_d[1]) *180 / np.pi
            roll = np.arctan2(y_d[0],y_d[2]) *180 / np.pi
            yaw = np.arctan2(-1 * x_d[1], z_d[1]) *180 / np.pi

            x = (camera_position[0])     #合計することでカメラ座標系の現在の座標
            y = (camera_position[1])
            z = (camera_position[2])
            print(x)       #合計することでカメラ座標系の現在の座標
            print(y)
            print(z)
            print("roll : " + str(roll))
            print("pitch: " + str(pitch))
            print("yaw  : " + str(yaw))
            cv2.imshow('drawDetectedMarkers', gazou)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

x = camera(img, dictionary)