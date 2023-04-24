import cv2
from picamera2 import Picamera2
from libcamera import controls


class Picam():
    def __init__(self):
        # define camera parameter
        size = (640, 480)

        # setting picam2 up
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"format": 'XRGB8888', "size": size})
        self.picam2.align_configuration(config)
        self.picam2.configure(config)
        self.picam2.start()

        # Libcamera's setting to use AF mode
        self.picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

        # Libcamera's setting to use AF mode (AFSpeed Fast)
        # picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous,"AFSeed":controls.AfSpeedEnum.Fast})



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
