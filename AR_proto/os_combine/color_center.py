import cv2
import numpy as np

hsv_coef = np.array([1/2, 2.55, 2.55])
LOW_COLOR_EDIT = {1:np.array([300, 59, 45]),0:np.array([200, 40, 70]),99:np.array([36, 90, 59])}
HIGH_COLOR_EDIT = {1:np.array([360, 100, 100]),0:np.array([250, 100, 100]),99:np.array([42, 100, 100])}
    
LOW_COLOR = {k:np.round(LOW_COLOR_EDIT[k]*hsv_coef) for k in LOW_COLOR_EDIT.keys()}
HIGH_COLOR = {k:np.round(HIGH_COLOR_EDIT[k]*hsv_coef) for k in HIGH_COLOR_EDIT.keys()}
    

def capture_image():
    # カメラを起動
    cap = cv2.VideoCapture(1)  # 0はデフォルトのカメラデバイスを指定

    # カメラが正常に起動したかチェック
    if not cap.isOpened():
        print("カメラが正常に起動できませんでした。")
        cap.release()
        return

    # 画像を取得
    ret, frame = cap.read()

    # 画像の取得に成功したかチェック
    if not ret:
        print("画像の取得に失敗しました。")
        cap.release()
        return

    # 画像を保存
    image_path = "./captured_image.jpg"
    cv2.imwrite(image_path, frame)

    print("画像を取得しました。")
    cap.release()
capture_image()

def find_color_centroid(image, color_lower, color_upper):
    # 画像をBGRからHSVに変換
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 特定の色範囲のマスクを作成
    mask = cv2.inRange(hsv_image, color_lower, color_upper)

    # マスクされた画像の重心を計算
    m = cv2.moments(mask)
    if m["m00"] != 0:
        center_x = int(m["m10"] / m["m00"])
        center_y = int(m["m01"] / m["m00"])
        return center_x, center_y
    else:
        return None

# 画像のパスを指定
image_path = "./captured_image.jpg"
# image_path = "./color.jpg"

# 特定の色範囲を定義 (例: 赤色の範囲)

# 画像を読み込み
image = cv2.imread(image_path)

# 画像中の特定の色を含む画素の重心を求める
centroid = find_color_centroid(image, LOW_COLOR[0], HIGH_COLOR[0])

if centroid is not None:
    print(f"特定の色を含む画素の重心: ({centroid[0]}, {centroid[1]})")
else:
    print("特定の色を含む画素が見つかりませんでした。")


    
def draw_point(image, x, y):
    # 画像に点を描画する
    point_color = (0, 0, 255)  # 赤色の点を指定 (BGRで指定)
    thickness = -1  # 塗りつぶし
    radius = 5  # 点の半径
    cv2.circle(image, (x, y), radius, point_color, thickness)

# 画像を読み込み
image = cv2.imread(image_path)

# 画像に点を描画
draw_point(image, centroid[0], centroid[1])

# 画像を表示
cv2.imshow('Image with Point', image)

# キー入力を待つ
cv2.waitKey(0)

# ウィンドウを閉じる
cv2.destroyAllWindows()