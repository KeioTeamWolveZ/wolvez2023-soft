"""
Take a picture or movie
"""
"""
from picamera2 import Picamera2
import cv2
picam2 = Picamera2()

#image
#picam2.start_and_capture_file("test.jpg")

#movie (5s)
#picam2.start_and_record_video("test.mp4", duration=5)
"""

"""
Display for input data in real -time
*ImportError: numpy.core.multiarray failed to import
  -> "pip install -U numpy"
"""
"""
import cv2
from picamera2 import Picamera2
from libcamera import controls

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()
#Libcamera's setting to use AF mode
#picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
#Libcamera's setting to use AF mode (AFSpeed Fast)
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous,"AFSeed":controls.AfSpeedEnum.Fast})

#Display for input data in real -time 
while True:
  im = picam2.capture_array()
  cv2.imshow("Camera", im)
 
  key = cv2.waitKey(1)
  #If you push "esc-key", this roop is finished.
  if key == 27:
    break

picam2.stop()
cv2.destroyAllWindows()
"""
