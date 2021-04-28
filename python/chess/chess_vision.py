import cv2
import chess
import numpy as np
import imutils
import time
import apriltag

# GREEN = BLACK
# ORANGE = WHITE

SQUARE_SIZE = 60
BOARD_SIZE = SQUARE_SIZE * 8

def gstreamer_pipeline(
    capture_width=3280,
    capture_height=2464,
    display_width=820,
    display_height=616,
    framerate=20,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

options = apriltag.DetectorOptions(families="tag36h11")
detector = apriltag.Detector(options)

class ChessCamera(object):
    def __init__(self):
        self._capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
        self._color_detector = SquareColorDetector()

    def current_chessboard_frame(self):
        _, frame = self._capture.read()
        # cam = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
        # _, frame = cam.read()
        h, w = frame.shape[:2]

        M = get_chessboard_perspective_transform(frame)
        bgr_img = cv2.warpPerspective(frame, M, (BOARD_SIZE+2*SQUARE_SIZE,BOARD_SIZE))
        # cv2.imshow('hi', bgr_img)
        # cv2.waitKey()
        # cam.release()
        return ChessboardFrame(bgr_img)

    def current_colored_board_mask(self):
        cbf = self.current_chessboard_frame()
        cbm = [None] * 64

        # loop through each square and detect the color of the piece
        for i in range(64):
            sq = cbf.square_at(i)
            cbm[i] = self._color_detector.detect(sq)
        return cbm


class SquareColorDetector(object):
    def detect(self, square):
        # these may need adjusting in different lightings
        green_lower = (47, 74, 0)
        green_upper = (81, 247, 255)
        orange_lower = (0, 74, 0) 
        orange_upper = (15,247,255)
        green_radius = color_filter(square, green_lower, green_upper)
        orange_radius = color_filter(square, orange_lower, orange_upper)

        # decide the occupancy of the square based on the size of the contours found
        if (int(green_radius) < 10 and int(orange_radius) < 10):
            return None
        elif (int(green_radius) > int(orange_radius)):
            return chess.BLACK
        else:
            return chess.WHITE
    

class ChessboardFrame():
    def __init__(self, img):
        self.img = img

    def square_at(self, i):
        y = BOARD_SIZE - (int(i / 8) % 8) * SQUARE_SIZE - SQUARE_SIZE
        x = ((i % 8) * SQUARE_SIZE) + SQUARE_SIZE
        return Square(i, self.img[y:y+SQUARE_SIZE, x:x+SQUARE_SIZE, :])


class Square(object):
    def __init__(self, position, raw_img):
        self.position = position
        self.raw_img = raw_img


def get_chessboard_perspective_transform(frame):
    try:
        M = np.load('chessboard_perspective_transform.npy')
        return M
    except:
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        image_corners = np.float32([[0,0], [BOARD_SIZE+2*SQUARE_SIZE,0], [0,BOARD_SIZE], [BOARD_SIZE+2*SQUARE_SIZE,BOARD_SIZE]])

        # cv2.imshow('img', gray)
        # cv2.waitKey()

        # brighter_img = cv2.convertScaleAbs(gray, alpha=1.95, beta=-20)

        # cv2.imshow('brighter', brighter_img)
        # cv2.waitKey()

        april_results = detector.detect(gray)
        april_centers = []
        for tag in april_results:
            april_centers.append([tag.center[0], tag.center[1]])
            # print(tag.tag_id)
        # the found corners are one square in from the edge diagonally
        # calculate the approximate positions of them from other corners
        # p1 = board_corners[0][0]
        # p2 = board_corners[8][0]
        # delX = abs(p1[0] - p2[0])
        # delY = abs(p1[1] - p2[1])

        # edge_top_left = [board_corners[0][0][0] - delX, board_corners[0][0][1] - delY]
        # edge_top_right = [board_corners[6][0][0] + delX, board_corners[6][0][1] - delY]
        # edge_bot_left = [board_corners[42][0][0] - delX, board_corners[42][0][1] + delY]
        # edge_bot_right = [board_corners[48][0][0] + delX, board_corners[48][0][1] + delY]

        edge_corners = np.array(april_centers, np.float32)
        # print(edge_corners)
        # print(image_corners)
        M = cv2.getPerspectiveTransform(edge_corners, image_corners)
        np.save('chessboard_perspective_transform.npy', M)
        return M


def color_filter(frame, lower, upper):
    # string = 'square ' + str(frame.position)
    # cv2.imshow(string, frame.raw_img)
    # cv2.waitKey()

    # blur/convert to HSV
    blurred = cv2.GaussianBlur(frame.raw_img, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        return radius

    return 0