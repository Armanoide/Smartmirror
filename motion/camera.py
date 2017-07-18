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
            picameraA = __import__('picamera.array', fromlist=[''])
            self.camera = picamera.PiCamera()
            self.camera.resolution = (self.width, self.height)
            self.camera.framerate = 32
            self.rawCapture = picameraA.PiRGBArray(self.camera, size=(self.width, self.height))
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
                num_rows, num_cols = self.frame.shape[:2]
                rotation_matrix = cv2.getRotationMatrix2D((num_cols / 2, num_rows / 2), 90, 1)
                self.frame = cv2.warpAffine(self.frame, rotation_matrix, (num_cols, num_rows))
                self.frame = cv2.flip(self.frame, 1)
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
