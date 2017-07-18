import cv2
import numpy as np
import time
from enum import Enum
import base64

font = cv2.FONT_HERSHEY_SIMPLEX


def is_list_upper(list_a, list_b):
    """ return positive when list_a > 0 """
    diff = 0
    len_a = len(list_a)
    len_b = len(list_b)
    i = 0
    if len_b < len_a:
        i = len_b - 1
    else:
        i = len_a - 1
    while i > 0:
        if list_a[i] > list_b[i]:
            diff += 1
        if list_a[i] < list_b[i]:
            diff -= 1
        i -= 1
    return diff


def get_average_hvs_list(list_hsv):
    h, v, s, i = 0, 0, 0, 0
    size = len(list_hsv)
    while i < size:
        h += list_hsv[i][0]
        s += list_hsv[i][1]
        v += list_hsv[i][2]
        i += 1
    h /= size
    v /= size
    s /= size
    return [h, s, v]


class HandSkinStatus(Enum):
    OFF = 0
    STANDBY = 1
    RECORDING = 2
    DETECTION = 3
    IN_USE = 4


class HandSkin(object):
    def __init__(self, width, height):

        self.hvs_skin_color = None
        self.stock_record_skin = []
        self.h_min = -1
        self.v_min = -1
        self.s_min = -1

        self.h_max = -1
        self.v_max = -1
        self.s_max = -1

        self.width = width
        self.height = height
        self.frame = None
        self.debug_mode = False
        self.last_update = int(time.time())
        self.last_update_no_detecting_hand = None
        self.background = None
        self.status = HandSkinStatus.OFF
        self.last_status = HandSkinStatus.IN_USE
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.center = None
        self.kernel_square = np.ones((6, 6), np.uint8)
        self.kernel_ellipse_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.kernel_ellipse_big = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))

        self.socketIO = None

        self.count_circle_convex = 0
        self.last_count_circle_convex = 0

    def _h_min(self, x):
        self.h_min = x

    def _s_min(self, x):
        self.s_min = x

    def _v_min(self, x):
        self.v_min = x

    def _h_max(self, x):
        self.h_max = x

    def _s_max(self, x):
        self.s_max = x

    def _v_max(self, x):
        self.v_max = x

    def set_frame(self, frame):
        self.frame = frame.copy()

    def notify_status_changed(self):
        if self.socketIO is not None:
            json = {"status": str(self.status)}
            self.socketIO.emit('set_status', json)

    def notify_with_image(self, frame):
        if self.socketIO is not None:
            frame = cv2.imencode('.jpeg', frame)[1]
            frame = bytearray(frame)
            frame = str(base64.b64encode(frame))
            frame = str(frame.encode('utf-8'))
            self.socketIO.emit('set_hsv_img', {'hsv_img': frame})

    def set_debug(self, debug):
        self.debug_mode = debug
        if debug:
            # work bug Segmentation fault: 11 after 30s
            if True is False:
                cv2.namedWindow('HSV_TrackBarMIN')
                cv2.createTrackbar('h_min', 'HSV_TrackBarMIN', 0, 255, self._h_min)
                cv2.createTrackbar('s_min', 'HSV_TrackBarMIN', 0, 255, self._s_min)
                cv2.createTrackbar('v_min', 'HSV_TrackBarMIN', 0, 255, self._v_min)
                cv2.namedWindow('HSV_TrackBarMAX')
                cv2.createTrackbar('h_max', 'HSV_TrackBarMAX', 0, 255, self._h_max)
                cv2.createTrackbar('s_max', 'HSV_TrackBarMAX', 0, 255, self._s_max)
                cv2.createTrackbar('v_max', 'HSV_TrackBarMAX', 0, 255, self._v_max)

                print("HSV MIN")
                # best match 0
                print(self.h_min)
                # best mach 44
                print(self.s_min)
                # best match 61
                print(self.v_min)

                print("HSV MAX")
                # best match 20
                print(self.h_max)
                # best match 255
                print(self.s_max)
                # best match 255
                print(self.v_max)

    def process(self):
        if self.status is HandSkinStatus.STANDBY \
                or self.status is HandSkinStatus.RECORDING \
                or self.status is HandSkinStatus.DETECTION \
                or self.status is HandSkinStatus.IN_USE:
            self.get_hand_skin()
        else:
            self.waiting_user()
        if self.status is not self.last_status:
            self.last_status = self.status
            self.notify_status_changed()

    def waiting_user(self):
        frame = self.frame.copy()
        # BLUR
        frame = self.fgbg.apply(frame)
        self.last_update = int(time.time())
        ret, thresh = cv2.threshold(frame, 127, 255, 0)
        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.stock_record_skin = []
        if self.debug_mode:
            pass
            #cv2.imshow('waiting_user', frame)
        print("waiting_user")
        print(len(contours))
        if len(contours) > 900:
            self.status = HandSkinStatus.STANDBY

    def get_hand_skin(self):

        print(self.status)
        frame = self.frame.copy()
        # BLUR
        gaussian_blur = cv2.GaussianBlur(frame, (1, 1), 0)
        # HSV
        hsv = cv2.cvtColor(gaussian_blur, cv2.COLOR_BGR2HSV)
        color = hsv[self.width / 2, self.height / 2]
        now = int(time.time())
        if self.status is HandSkinStatus.STANDBY and now - self.last_update > 3:
            self.last_update = now
            self.status = HandSkinStatus.RECORDING
            return

        if self.status is HandSkinStatus.STANDBY:
            if self.debug_mode:
                cv2.circle(frame, (int(self.width / 2), int(self.height / 2)), 2, [0, 0, 255], 2)
                self.notify_with_image(frame)
                #cv2.imshow("mask_hsv", frame)
            return

        if self.status is HandSkinStatus.RECORDING and now - self.last_update > 5:
            self.last_update = now
            self.status = HandSkinStatus.DETECTION
            self.last_update_no_detecting_hand = now
            self.hvs_skin_color = get_average_hvs_list(self.stock_record_skin)

            self.h_min = self.hvs_skin_color[0] - 25
            self.s_min = self.hvs_skin_color[1] - 25
            self.v_min = self.hvs_skin_color[2] - 25

            self.h_max = self.hvs_skin_color[0] + 25
            self.s_max = self.hvs_skin_color[1] + 25
            self.v_max = self.hvs_skin_color[2] + 25

            if self.debug_mode:
                cv2.circle(frame, (int(self.width / 2), int(self.height / 2)), 2, [0, 0, 255], 2)
                #cv2.imshow("mask_hsv", frame)
            return

        if self.status is HandSkinStatus.RECORDING:
            self.stock_record_skin.append(color)
            if self.debug_mode:
                cv2.circle(frame, (int(self.width / 2), int(self.height / 2)), 2, [0, 0, 255], 2)
                self.notify_with_image(frame)
                #cv2.imshow("mask_hsv", frame)

            return

        # Get skin color
        mask_hsv = cv2.inRange(hsv,
                               np.array([self.h_min, self.s_min, self.v_min]),
                               np.array([self.h_max, self.s_max, self.v_max]))
        cv2.circle(frame, (int(self.width / 2), int(self.height / 2)), 2, [0, 0, 255], 2)
        if self.debug_mode:
            #cv2.imshow("frame frame", frame)
            #cv2.imshow("mask_hsv", mask_hsv)
            self.notify_with_image(mask_hsv)

        # Improve morphology with dilation and erode
        dilation_1 = cv2.dilate(mask_hsv, self.kernel_ellipse_small, iterations=1)
        if self.debug_mode:
            #cv2.imshow("dilation_1", dilation_1)
            pass

        erosion_1 = cv2.erode(dilation_1, self.kernel_square, iterations=1)
        if self.debug_mode:
            #cv2.imshow("erosion_1", erosion_1)
            pass

        dilation_2 = cv2.dilate(erosion_1, self.kernel_ellipse_small, iterations=1)
        if self.debug_mode:
            #cv2.imshow("dilation_2", dilation_2)
            pass

        clean_noise_1 = cv2.medianBlur(dilation_2, 5)
        if self.debug_mode:
            #cv2.imshow("clean_noise_1", clean_noise_1)
            pass

        dilation_3 = cv2.dilate(clean_noise_1, self.kernel_ellipse_big, iterations=1)
        if self.debug_mode:
            #cv2.imshow("dilation_3", dilation_3)
            pass

        dilation_4 = cv2.dilate(dilation_3, self.kernel_ellipse_small, iterations=1)
        if self.debug_mode:
            #cv2.imshow("dilation_4", dilation_4)
            pass
        # Remove noise

        clean_noise_2 = cv2.medianBlur(dilation_3, 21)
        if self.debug_mode:
            #cv2.imshow("clean_noise_2", clean_noise_2)
            pass

        self.detect_palm_and_finger(clean_noise_2)

        print(self.count_circle_convex)
        if self.status is HandSkinStatus.DETECTION \
                and self.count_circle_convex == 4:
            self.status = HandSkinStatus.IN_USE

        if self.status is HandSkinStatus.DETECTION \
                and self.count_circle_convex == 0 and self.last_update_no_detecting_hand is None:
            self.last_update_no_detecting_hand = int(time.time())

        if self.status is HandSkinStatus.DETECTION \
                and self.count_circle_convex == 0 and self.last_update_no_detecting_hand is not None \
                and now - self.last_update_no_detecting_hand > 5:
            self.status = HandSkinStatus.OFF
            self.last_update_no_detecting_hand = None
            self.last_update = now
            self.fgbg = cv2.createBackgroundSubtractorMOG2()

    def detect_palm_and_finger(self, frame):
        original = self.frame.copy()
        ret, thresh = cv2.threshold(frame, 127, 255, 0)
        if self.debug_mode:
            #cv2.imshow('thresh', thresh)
            pass

        im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # extract large contour
        ci = None
        max_area = 250
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if area > max_area:
                max_area = area
                ci = i

        self.center = None
        if ci is not None:
            cnt = contours[ci]
            hull = cv2.convexHull(cnt)
            moments = cv2.moments(cnt)

            if moments['m00'] != 0:
                cx = int(moments['m10'] / moments['m00'])  # cx = M10/M00
                cy = int(moments['m01'] / moments['m00'])  # cy = M01/M00

            center = (cx, cy)
            self.center = center
            if self.debug_mode:
                cv2.circle(original, center, 2, [255, 255, 0], 2)

            # draw contour
            cv2.drawContours(original, [cnt], 0, (0, 255, 255), 2)
            cv2.drawContours(original, [hull], 0, (0, 0, 255), 2)

            x, y, w, h = cv2.boundingRect(cnt)
            _ = cv2.rectangle(original, (x, y), (x + w, y + h), (0, 255, 0), 2)

            self.count_circle_convex = 0
            cnt = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
            hull = cv2.convexHull(cnt, returnPoints=False)
            defects = cv2.convexityDefects(cnt, hull)
            if defects is not None and len(defects.shape) > 0:
                for i in range(defects.shape[0]):
                    s, e, f, d = defects[i, 0]
                    start = tuple(cnt[s][0])
                    end = tuple(cnt[e][0])
                    far = tuple(cnt[f][0])
                    cv2.line(original, start, end, [0, 255, 0], 2)
                    cv2.circle(original, far, 5, [255, 153, 51], 3)
                    self.count_circle_convex += 1

                hull = cv2.convexHull(cnt, returnPoints=True)
                nb_fingers = len(hull) - 2
                # print(nb_fingers)
                for i in range(len(hull)):
                    [x, y] = hull[i][0].flatten()
                    coord = (int(x), int(y))
                    cv2.circle(original, coord, 2, [0, 255, 0], -1)
                    cv2.circle(original, coord, 5, [45, 255, 45], -1)
                    cv2.circle(original, coord, 8, [102, 44, 245], -1)
                    cv2.putText(original, 'finger' + str(i), coord, font, 0.5, (255, 255, 255), 2)

            if self.last_count_circle_convex is not self.count_circle_convex:
                if self.socketIO is not None:
                    self.last_count_circle_convex = self.count_circle_convex
                    json = {'count_circle_convex': str(self.count_circle_convex)}
                    self.socketIO.emit('set_count_circle_convex', json)

        if self.debug_mode:
            #cv2.imshow("display_contour_debug", original)
            pass