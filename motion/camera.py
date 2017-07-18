##########
########## To use pi cam uncomment
##########
#from picamera import PiCamera
#from picamera.array import PiRGBArray

import cv2
import time

ESC = 27


class Camera(object):
    def __init__(self, is_picamera=False, width=600, height=600):

        self.is_picamera = is_picamera
        self.frame = None
        self.width = width
        self.height = height
        print("is_picamera")

        if is_picamera:
            picamera = __import__('picamera', fromlist=[''])
            self.camera = picamera.PiCamera()
            self.camera.resolution = (self.width, self.height)
            self.camera.framerate = 32
            self.rawCapture = picamera.PiRGBArray(self.camera, size=(self.width, self.height))
            time.sleep(0.1)

        else:
            self.cap = cv2.VideoCapture(1)  # 1 or 0
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def get_frame(self):

        if self.is_picamera:
            self.rawCapture.seek(0)  # Added these line
            self.rawCapture.truncate()  # This too
            for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
                self.frame = frame.array
                break
        else:
            ret, img = self.cap.read()
            if ret is not None:
                img = cv2.flip(img, 1)
                self.frame = img
            else:
                self.frame = None

    def is_cam_open(self):
        key = cv2.waitKey(1)
        if self.is_picamera:
            return True and key != ESC
        else:
            return self.cap.isOpened() and key != ESC
