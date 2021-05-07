from gtts import gTTS
import os
from playsound import playsound
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
FRAME_COUNT = 150

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
        self.relocate_board = True
        self.frames_read = 0

    def current_chessboard_frame(self):
        _, frame = self._capture.read()
        h, w = frame.shape[:2]

        M = get_chessboard_perspective_transform(frame, self.relocate_board)
        bgr_img = cv2.warpPerspective(frame, M, (BOARD_SIZE+2*SQUARE_SIZE,BOARD_SIZE))
        self.increment_frame_count()

        return ChessboardFrame(bgr_img)

    def increment_frame_count(self):
        self.frames_read = self.frames_read + 1
        if self.frames_read == FRAME_COUNT:
            self.relocate_board = True
            self.frames_read = 0
        else:
            self.relocate_board = False

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
        green_lower = (47, 74, 80)
        green_upper = (81, 247, 255)
        orange_lower = (0, 122, 76) 
        orange_upper = (14,197,255)
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


def get_chessboard_perspective_transform(frame, relocate_tags):
    if relocate_tags:
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            image_corners = np.float32([[0,0], [BOARD_SIZE+2*SQUARE_SIZE,0], [0,BOARD_SIZE], [BOARD_SIZE+2*SQUARE_SIZE,BOARD_SIZE]])

            april_results = detector.detect(gray)
            april_centers = []
            for tag in april_results:
                april_centers.append([tag.center[0], tag.center[1]])
                
            edge_corners = np.array(april_centers, np.float32)
            
            M = cv2.getPerspectiveTransform(edge_corners, image_corners)
            np.save('chessboard_perspective_transform.npy', M)
            return M
        except:
            # if something is obstructing one of the tags, just load the old transform
            M = np.load('chessboard_perspective_transform.npy')
            return M
    else:
        M = np.load('chessboard_perspective_transform.npy')
        return M


def color_filter(frame, lower, upper):
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


def piece_list(board, color):
    pieces = []
    valid_piece_types = [chess.KING, chess.QUEEN, chess.BISHOP, chess.ROOK, chess.KNIGHT, chess.PAWN]
    for piece_type in valid_piece_types:
        pieces.append(list(chess.BaseBoard.pieces(board, piece_type, color)))
    pieces = sorted(sum(pieces, []))
    return pieces


def speak(speak_string):
    myobj = gTTS(text=speak_string, lang='en', slow=False)
    myobj.save('audio.mp3')
    playsound('audio.mp3')
    os.remove('audio.mp3')


def declare_winner(board, color):
    if board.is_game_over():
        outcome = board.result()
        if outcome == '1/2-1/2':
            speak('Good game. Its a draw.')
        elif outcome == '1-0' and color:
            speak("Good job. You beat me.")
        elif outcome == '0-1' and not color:
            speak("Good job. You beat me.")
        else:
            speak('You lost. Get better.')
    else:
        speak('The game was not over, but you were losing.')
    

