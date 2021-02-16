from cv2 import cv2
import  numpy
from imutils.video import VideoStream
import imutils
import time

time.sleep(2.0)
vs = VideoStream(0)
    #.start()

while True:
    frame = vs.read()
    # frame = frame[1]
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('Frame', gray) 

    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

print('hello')