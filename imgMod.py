import cv2
import numpy as np

WHITE = 255
BLACK = 0
THRESH = 127

def cropImage(frame,sizeX,sizeY):
	size = frame.shape
	x1 = (size[0] - sizeX)//2
	x2 = x1 + sizeX
	y1 = (size[1] - sizeY)//2
	y2 = y1 + sizeY
	return frame[x1:x2,y1:y2]

def redMask(frame):
	min1 = np.uint8([[0,50,50]])
	max1 = np.uint8([[10,255,255]])
	min2 = np.uint8([[163,50,50]])
	max2 = np.uint8([[180,255,255]])
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

	newHSV = cv2.add(cv2.inRange(hsv,min1,max1), cv2.inRange(hsv,min2,max2))
	return newHSV

def erode(image,strength):
	return cv2.erode(image,np.ones((strength,strength), np.uint8))

def dilate(image,strength):
	return cv2.dilate(image,np.ones((strength,strength), np.uint8))

def open(image, strength):
	return(dilate(erode(image, strength), strength))

def close(image, strength):
	return(erode(dilate(image, strength), strength))

def binary(image):
	imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	ret,thresh = cv2.threshold(imgray,127,255,0)
	return thresh

def blur(image, strength):
	return cv2.GaussianBlur(image,(strength*2 + 1,strength*2 + 1),5)
