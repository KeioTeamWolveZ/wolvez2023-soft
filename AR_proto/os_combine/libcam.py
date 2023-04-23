import cv2
from picamera2 import Picamera2
from libcamera import controls


class Picam():
    def __init__(self):
        # define camera parameter
        size = (640, 480)

        # setting picam2 up
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"format": 'XRGB8888', "size": size})
        picam2.align_configuration(config)
        picam2.configure(config)
        picam2.start()

        # Libcamera's setting to use AF mode
        picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

        # Libcamera's setting to use AF mode (AFSpeed Fast)
        # picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous,"AFSeed":controls.AfSpeedEnum.Fast})
        return picam2


if __name__ == "__main__":
    # Display for input data in real -time
    picam2 = Picam()
    while True:
        im = picam2.capture_array()
        cv2.imshow("Camera", im)

        key = cv2.waitKey(1)
        # If you push "esc-key", this roop is finished.
        if key == 27:
            cv2.imwrite("test_cv2.jpg", im)
            break
    picam2.stop()
    cv2.destroyAllWindows()
