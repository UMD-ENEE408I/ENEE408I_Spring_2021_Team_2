import cv2
import chess
import numpy as np
# from chess_contour import ColorFilter

# GREEN = WHITE
# ORANGE = BLACK

SQUARE_SIZE = 60
BOARD_SIZE = SQUARE_SIZE * 8

def gstreamer_pipeline(
    capture_width=3280,
    capture_height=2464,
    display_width=1640,
    display_height=1232,
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

class ChessCamera(object):
    def __init__(self):
        self._capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
        # self._capture = cv2.VideoCapture(0)
        self._color_detector = SquareColorDetector()

    def current_chessboard_frame(self):
        _, frame = self._capture.read()
        
        # frame = frame[1]
        h, w = frame.shape[:2]

        # print(frame)
        # while True:
        #     _, frame = self._capture.read()
        #     cv2.imshow("test",frame)
        #     cv2.waitKey()
        M = get_chessboard_perspective_transform(frame)
        bgr_img = cv2.warpPerspective(frame, M, (BOARD_SIZE,BOARD_SIZE))
        img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        cv2.imshow("test2",img)
        return ChessboardFrame(img)

    def current_colored_board_mask(self):
        cbf = self.current_chessboard_frame()
        cbm = [None] * 64
        for i in range(64):
            sq = cbf.square_at(i)
            cbm[i] = self._color_detector.detect(sq)
        return cbm

def get_chessboard_perspective_transform(frame):
    try:
        M = np.load('chessboard_perspective_transform.npy')
        return M
    except:
        board_size = (7,7)
        # _, frame = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER).read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # while True:
        #     # _, frame = self._capture.read()
        #     cv2.imshow("test",gray)
        #     cv2.waitKey()
        found, board_corners = cv2.findChessboardCorners(gray, board_size)
        print('poop')
        image_corners = np.float32([[0,0], [BOARD_SIZE,0], [0,BOARD_SIZE], [BOARD_SIZE,BOARD_SIZE]])
        assert found, "Couldn't find chessboard."

        M = cv2.getPerspectiveTransform(board_corners, image_corners)
        np.save('chessboard_perspective_transform.npy', M)
        return M


class SquareColorDetector(object):
    def detect(self, square):
        green_lower = (22, 115, 64)
        green_upper = (76, 216, 187)
        orange_lower = (0, 139, 97) # FILL THESE OUT WHEN THE PIECES ARRIVE
        orange_upper = (39,255,239)
        green_radius = ColorFilter(square, green_lower, green_upper)
        orange_radius = ColorFilter(square, orange_lower, orange_upper)

        if (int(green_radius) < 10 and int(orange_radius) < 10):
            return None
        elif (int(green_radius) > int(orange_radius)):
            return chess.WHITE
        else:
            return chess.BLACK

class ChessboardFrame():
    def __init__(self, img):
        self.img = img

    def square_at(self, i):
        y = BOARD_SIZE - ((i / 8) % 8) * SQUARE_SIZE - SQUARE_SIZE
        x = (i % 8) * SQUARE_SIZE
        return Square(i, self.img[y:y+SQUARE_SIZE, x:x+SQUARE_SIZE, :])

class Square(object):
    def __init__(self, position, raw_img):
        self.position = position
        self.raw_img = raw_img

def colorFilter(self, frame, lower, upper):
    # def largest_contour(self, frame, lower, upper):
    # blur it and convert it to the HSV color space
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color, then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, lower, upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        return radius

    return 0