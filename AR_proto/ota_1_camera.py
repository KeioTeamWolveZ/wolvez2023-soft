import numpy as np
import cv2
from cv2 import aruco

def main():
    cap = cv2.VideoCapture('画像のパス')
    ##cap = cv2.VideoCapture(0)   #PCのかめら
    # マーカーサイズ
    marker_length = 0.056 # [m]
    # マーカーの辞書選択
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)  #ARマーカーの生成に使用
    #aruco.customDictionary(nMakers(ID数),Markersize,baseDictionary(基本となるディクショナリ))で独自のディクショナリ作成も可能

    #レンズの性質などの内部パラメータ
    camera_matrix = np.load("mtx.npy")
    distortion_coeff = np.load("dist.npy")

    while True:
        ret, img = cap.read()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(img, dictionary)  #画像とディクショナリを指定して検出したマーカーの各頂点の座標を含む配列のリスト、マーカーのIDの配列、されなかったものの配列の三つを返す
                                                                                #書かれてないけどこの関数でcamera_matrixとdistortion_coeffを使用している(デフォルトではnoneになってる)
        # 可視化
        aruco.drawDetectedMarkers(img, corners, ids, (0,255,255))

        if len(corners) > 0:
            # マーカーごとに処理
            for i, corner in enumerate(corners):
                # rvec -> rotation vector, tvec -> translation vector
                rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corner, marker_length, camera_matrix, distortion_coeff)  #マーカーごとに外部パラメータ(回転ベクトルと並進ベクトル)を算出

                # < rodoriguesからeuluerへの変換 >

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

                # 可視化
                ##draw_pole_length = marker_length/2 # 現実での長さ[m]
                ##aruco.drawAxis(img, camera_matrix, distortion_coeff, rvec, tvec, draw_pole_length)

        cv2.imshow('drawDetectedMarkers', img)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
