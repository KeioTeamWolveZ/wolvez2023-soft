"""
Take a movie
"""

from picamera2 import Picamera2
import cv2
picam2 = Picamera2()

#movie (10s)
picam2.start_and_record_video("test.mp4", duration=10)
