"""
Take a picture
"""
from picamera2 import Picamera2
import cv2

# image without any setting and cv2
picam2 = Picamera2()
picam2.start_and_capture_file("test.jpg")
picam2.stop()
cv2.destroyAllWindows()

# setting picam2 up
#picam2 = Picamera2()
#config = picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (4000, 3500)})
#picam2.align_configuration(config)
#picam2.configure(config)

#picam2.start()
#Libcamera's setting to use AF mode
#picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})

# save with cv2
#im = picam2.capture_array()
#cv2.imwrite("test_cv2.jpg", im)
#picam2.stop()
#cv2.destroyAllWindows()
