import cv2
import math
from hand_skin import HandSkin
from hand_skin import HandSkinStatus
from enum import Enum
import time
import threading

ESC = 27


class GestureDirectionHorizontal(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2


class GestureDirectionVertical(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    UP_MIDDLE = 3
    DOWN_MIDDLE = 4


class GestureControlMenu(Enum):
    TO_SELECT = 0


class GestureControl(object):
    def __init__(self):
        print(cv2.__version__)
        self.DEBUG = True
        self.width = 600
        self.height = 600
        self.socketIO = None

        self.cap = cv2.VideoCapture(1)  # 1 or 0
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)


        self.hand_skin = HandSkin(self.width, self.height)
        self.frame = None
        self.menu = GestureControlMenu.TO_SELECT
        self.last_center = None
        self.gesture_vertical = GestureDirectionVertical.NONE
        self.gesture_horizontal = GestureDirectionHorizontal.NONE
        self.position_hand_horizontal = GestureDirectionHorizontal.NONE
        self.position_hand_vertical = GestureDirectionVertical.NONE
        self.last_position_hand_vertical = GestureDirectionVertical.NONE
        self.last_position_hand_horizontal = GestureDirectionHorizontal.NONE
        self.recording_gesture_horizontal = []
        self.recording_gesture_vertical = []
        self.last_update_detect_gesture = float(time.time())

    def is_cam_open(self):
        key = cv2.waitKey(1)
        return self.cap.isOpened() and key != ESC

    def close(self):
        cv2.destroyAllWindows()

    def get_frame(self):
        ret, img = self.cap.read()
        if ret is not None:
            img = cv2.flip(img, 1)
            self.frame = img
        else:
            self.frame = None

    def get_average_gesture(self, tab, none_value):
        if len(self.recording_gesture_horizontal) > 0:
            value = 0
            for i in tab:
                value += i
            if value == 0:
                value = none_value
            else:
                value = int(value / len(tab))
            return value

    def get_gesture(self):
        now = float(time.time())
        if now - self.last_update_detect_gesture > 1:
            self.last_update_detect_gesture = now
            v = self.get_average_gesture(
                    self.recording_gesture_horizontal,
                    0)
            if v is not None:
                self.gesture_vertical = GestureDirectionVertical(v)
            v = self.get_average_gesture(
                    self.recording_gesture_vertical,
                    0)
            if v is not None:
                self.gesture_horizontal = GestureDirectionHorizontal(v)
            if self.socketIO is not None:
                if self.last_position_hand_horizontal is not self.position_hand_horizontal:
                    self.last_position_hand_horizontal = self.position_hand_horizontal
                    json = {"position_hand_horizontal": str(self.position_hand_horizontal)}
                    self.socketIO.emit("set_position_hand_horizontal",json)

                if self.last_position_hand_vertical is not self.position_hand_vertical:
                    self.last_position_hand_vertical = self.position_hand_vertical
                    json = {"position_hand_vertical": str(self.position_hand_vertical)}
                    self.socketIO.emit("set_position_hand_vertical", json)
            self.recording_gesture_horizontal = []
            self.recording_gesture_vertical = []

            return


        if self.last_center is not None and self.hand_skin.center is not None:

            current_center_x, current_center_y = self.hand_skin.center
            last_center_x, last_center_y = self.last_center

            #if math.fabs(current_center_x - last_center_x) <= 5:
            #    current_center_x = last_center_x

            #if math.fabs(current_center_y - last_center_y) <= 5:
            #    current_center_y = last_center_y

            # if current_center_x == last_center_x and \
            #                current_center_y == last_center_y:
            #    self.gesture = None
            #    return

            if current_center_x >= self.width/2:
                self.position_hand_horizontal = GestureDirectionHorizontal.RIGHT
            if current_center_x <= self.width/2:
                self.position_hand_horizontal = GestureDirectionHorizontal.LEFT
            if current_center_y >= self.height/2:
                self.position_hand_vertical = GestureDirectionVertical.DOWN
            #if current_center_y >= self.height/2 and current_center_y <= self.height/2 + self.height/4:
            #    self.position_hand_vertical = GestureDirectionVertical.DOWN_MIDDLE
            if current_center_y <= self.height/2:
                self.position_hand_vertical = GestureDirectionVertical.UP_MIDDLE
            if current_center_y <= self.height/4:
                self.position_hand_vertical = GestureDirectionVertical.UP

            if last_center_y > current_center_y:
                self.recording_gesture_vertical.append(GestureDirectionVertical.UP.value)
                # self.gesture = GestureDirection.UP

            if last_center_y < current_center_y:
                self.recording_gesture_vertical.append(GestureDirectionVertical.DOWN.value)
                # self.gesture = GestureDirection.DOWN

            if last_center_x > current_center_x:
                self.recording_gesture_horizontal.append(GestureDirectionHorizontal.LEFT.value)
                # self.gesture = GestureDirection.LEFT

            if last_center_x < current_center_x:
                self.recording_gesture_horizontal.append(GestureDirectionHorizontal.RIGHT.value)
                # self.gesture = GestureDirection.RIGHT

        else:
            self.gesture_horizontal = GestureDirectionHorizontal.NONE
            self.gesture_vertical = GestureDirectionVertical.NONE
            self.position_hand_horizontal = GestureDirectionHorizontal.NONE
            self.position_hand_vertical = GestureDirectionVertical.NONE

        self.last_center = self.hand_skin.center

    def process(self):
        if self.hand_skin.status == HandSkinStatus.IN_USE:
            self.get_gesture()
            #print("self.gesture_vertical")
            #print(self.gesture_vertical)
            #print("self.gesture_horizontal")
            #print(self.gesture_horizontal)
            print("self.position_hand_horizontal")
            print(self.position_hand_horizontal)
            print("self.position_hand_vertical")
            print(self.position_hand_vertical)
            if self.menu is GestureControlMenu.TO_SELECT:
                pass

    def run(self):
        while self.is_cam_open():
            self.get_frame()
            self.hand_skin.socketIO = self.socketIO
            self.hand_skin.set_debug(self.DEBUG)
            self.hand_skin.set_frame(self.frame)
            self.hand_skin.process()
            self.process()
        self.close()