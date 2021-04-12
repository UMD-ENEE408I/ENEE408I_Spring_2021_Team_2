# import necessary packages
import imutils
import cv2

class ObjCenter:
	# def __init__(self, haarPath):
		# load OpenCV's Haar cascade face detector
		# self.detector = cv2.CascadeClassifier(haarPath)

	def update(self, frame, frameCenter):
		lower = (22, 53, 46)
		upper = (58, 255, 255)

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
		center = None

		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			cv2.circle(frame, (int(x), int(y)), int(radius),
            (0, 255, 255), 2)
			return ((x, radius), c)
		
		return (frameCenter, None)
















		# # convert the frame to grayscale
		# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# # detect all faces in the input frame
		# rects = self.detector.detectMultiScale(gray, scaleFactor=1.05,
		# 	minNeighbors=9, minSize=(30, 30),
		# 	flags=cv2.CASCADE_SCALE_IMAGE)
		# # check to see if a face was found
		# if len(rects) > 0:
		# 	# extract the bounding box coordinates of the face and
		# 	# use the coordinates to determine the center of the
		# 	# face
		# 	(x, y, w, h) = rects[0]
		# 	faceX = int(x + (w / 2.0))
		# 	faceY = int(y + (h / 2.0))
		# 	# return the center (x, y)-coordinates of the face
		# 	return ((faceX, faceY), rects[0])
		# # otherwise no faces were found, so return the center of the
		# # frame
		# return (frameCenter, None)

