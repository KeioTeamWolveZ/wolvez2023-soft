import cv2
from picamera2 import Picamera2
from libcamera import controls
import numpy as np

# setting picam2 up
picam2 = Picamera2()
# setting pix
picam2.senser_mode = 2
picam2.resolution = (640, 480)
#config = picam2.create_preview_configuration(main={"format": 'XRGB8888'})
config = picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (4000, 3600)})
#config = picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)})
picam2.align_configuration(config)
picam2.configure(config)

picam2.start()

#Libcamera's setting to use AF mode
#picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
#Libcamera's setting to use AF mode (AfSpeed Fast)
#picam2.set_controls({"AFSpeed":controls.AfSpeedEnum.Fast})
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous,"AfSpeed":controls.AfSpeedEnum.Fast})

#Display for input data in real -time 
while True:
  im = picam2.capture_array()
  cv2.imshow("Camera", im)
  key = cv2.waitKey(1)
  #If you push "esc-key", this roop is finished.
  if key == 27:
    cv2.imwrite("test_cv2.jpg", im)
    print(np.shape(im))
    break
picam2.stop()
cv2.destroyAllWindows()

