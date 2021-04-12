# import necessary packages
from objectCenter import ObjCenter
import signal
import serial
import time
import cv2

# begin serial connection
ser = serial.Serial('/dev/ttyUSB0')

# # function to handle keyboard interrupt
def signal_handler(sig, frame):
    print("[INFO] You pressed `ctrl + c`! Exiting...")
    ser.close()
    sys.exit()

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=60,
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

# signal trap to handle keyboard interrupt
signal.signal(signal.SIGINT, signal_handler)

# start the video stream and wait for the camera to warm up
vs = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
time.sleep(2.0)

# initialize the object center finder
obj = ObjCenter()

# left/right thresholds
x_thresholds = [(-2000, -300), (-300, -100), (-100, 100), (100, 300), (300, 2000)]

# fwd/back thresholds
r_thresholds = [(-250, -5), (-5, 10), (10, 40), (40, 100)]

# speeds
turn_speed = [-35, -20, 0, 20, 35]
fwd_speed = [-10, 0, 30, 50]

# loop indefinitely
while True:
    # grab the frame from the video stream
    frame = vs.read()
    frame = frame[1]

    # calculate the center of the frame
    (H, W) = frame.shape[:2]
    centerX = W // 2
    targetDepth = 75

    # find the object's location
    ball_Loc = obj.update(frame, (centerX, targetDepth))
    ((ball_X, ball_R), c) = ball_Loc
    
    # display the frame to the screen
    # cv2.imshow("Ball Tracking", frame)
    # cv2.waitKey(1)

    x_error = centerX - ball_X
    # find the threshold range that the x error falls into and set the motor speed difference accordingly
    for ind, bounds in enumerate(x_thresholds):
        if (bounds[0] <= x_error <= bounds[1]):
            pwm_diff = turn_speed[ind]

    r_error = targetDepth - ball_R
    # find the threshold range that the radius error falls into and set avg motor speed
    for ind, bounds in enumerate(r_thresholds):
        if (bounds[0] <= r_error <= bounds[1]):
            pwm_avg = fwd_speed[ind]

    ser.write(int(pwm_avg-pwm_diff).to_bytes(1, 'big', signed=True))
    ser.write(int(pwm_avg+pwm_diff).to_bytes(1, 'big', signed=True))

    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

vs.release()
ser.close()
