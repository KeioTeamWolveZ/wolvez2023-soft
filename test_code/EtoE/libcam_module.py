import cv2
from picamera2 import Picamera2
from libcamera import controls
from datetime import datetime


class Picam():
    def __init__(self):
        # define camera parameter
        self.size = (1750, 1300)

        # setting picam2 up
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"format": 'XRGB8888', "size": self.size})
        self.picam2.align_configuration(config)
        self.picam2.configure(config)
        self.picam2.start()

        # Libcamera's setting to use AF mode
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

        # Libcamera's setting to use AF mode (AFSpeed Fast)
        # self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous,"AfSpeed":controls.AfSpeedEnum.Fast})
        self.picam2.set_controls({"AfMode":0,"LensPosition":4.5})
        
    def capture(self, args, filename="test"):
        self.filename = filename
        """
        引数0→撮影&保存
        引数1→撮影のみ
        """
        # capture with libcam
        self.img = self.picam2.capture_array()
        self.img = self.img[:,:,:3]

        if args == 0:
            now = datetime.now()
            self.now = now.strftime('%Y%m%d%H%M%S')
            cv2.imwrite(filename + f"-{self.now}.jpg", self.img)
            # print(now)
            return self.img
        elif args == 1:
            # cv2.imshow("realtime", self.img)
            return self.img
        else:
            print("The argument should be 0 or 1")
            return None

    def show(self, img, title='realtime'):
        cv2.namedWindow(title,cv2.WINDOW_NORMAL)
        cv2.imshow(title,img)
        cv2.resizeWindow('realtime',640,480)
        
    def setup_video(self,name="video"):
        # 動画ファイル保存用の設定
        # fps = float(self.cap.get(cv2.CAP_PROP_FPS)) / 3                   # カメラのFPSを取得
        # w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))              # カメラの横幅を取得
        # h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))             # カメラの縦幅を取得
        v_size = (self.size[0]+300, self.size[1])
        #v_size = (self.size[0], self.size[1])
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')        # 動画保存時のfourcc設定（mp4用）
        # self.video = cv2.VideoWriter(f'{name}.mp4', fourcc, fps, (w+300, h))  # 動画の仕様（ファイル名、fourcc, FPS, サイズ）

        self.video = cv2.VideoWriter(f'{name}.mp4',fourcc,60,v_size)  # 動画の仕様（ファイル名、fourcc, FPS, サイズ）
        return self.video
    
    def red2blk(self,frame):
        self.red_thre = 50
        blk = frame
        condition_blue = blk[:,:,0] < self.red_thre
        condition_green = blk[:,:,1] < self.red_thre
        condition_red = blk[:,:,2] > self.red_thre
        blk[condition_blue * condition_green * condition_red] = 0
        cv2.imwrite(self.filename + f"-red2blk{self.now}.jpg", blk)
        return blk

    def write_video(self,frame):
        self.video.write(frame)   
        
    def stop(self):
        self.picam2.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Display for input data in real -time
    pc2 = Picam()
    while True:
        im = pc2.picam2.capture_array()
        print(im[:,:,:3].shape)
        cv2.imshow("Camera", im)

        key = cv2.waitKey(1)
        # If you push "esc-key", this roop is finished.
        if key == 27:
            cv2.imwrite("test_cv2.jpg", im)
            break
    pc2.picam2.stop()
    cv2.destroyAllWindows()
