import cv2
import numpy as np
import time
import imgMod
import math

WHITE = 255
BLACK = 0
THRESH = 127
TDELTA = 0.2

class UkeData(object):
	def __init__(self):
		self.holeSpot = (0,0)
		self.length = 0
		self.rot = 0
		self.fingers = []

def takeVideo():
	cam_index = 0
	cap = cv2.VideoCapture(cam_index)
	while(True):
		startTime = time.process_time()
		imgProcess(cap)
		endTime = time.process_time()
		time.sleep(0.5 + startTime - endTime)
		if(cv2.waitKey(10) == 27):
			break
	cap.release()
	cv2.destroyAllWindows()

def findUkulele(cap):
	ret, frame = cap.read()
	frame = imgMod.redMask(frame)
	frame = imgMod.erode(frame,10)
	frame = imgMod.dilate(frame,20)
	cv2.imshow("Uke",frame)

def testBlotches():
	image = cv2.imread("testImage1.png",0)

	startTime2 = time.process_time()
	blotchArray2 = imgMod.findBlotches(image,9)
	endTime2 = time.process_time()

	startTime1 = time.process_time()
	blotchArray = imgMod.fasterFindBlotches(image,9)
	endTime1 = time.process_time()
	
	slowTime = endTime2 - startTime2
	fastTime = endTime1 - startTime1
	print(slowTime)
	print(fastTime)
	print(slowTime-fastTime, "difference")
	print((1-(fastTime/slowTime))*100,"% Faster")

	newImage = image
	newImage = cv2.cvtColor(newImage,cv2.COLOR_GRAY2BGR)
	
	for blotch in blotchArray:
		newImage = cv2.circle(newImage,(int(blotch[1]),int(blotch[0])),int(blotch[2]),(0,255,0),3)
	cv2.imshow("test",newImage)

def imgProcess(cap):
	ret, frame = cap.read()
	frame = imgMod.redMask(frame)
	frame = imgMod.erode(frame,10)
	frame = imgMod.dilate(frame,20)
	blotchArray = imgMod.fasterFindBlotches(frame,20)
	newFrame = cv2.cvtColor(frame,cv2.COLOR_GRAY2BGR)
	for blotch in blotchArray:
		newFrame = cv2.circle(newFrame,(int(blotch[1]),int(blotch[0])),int(blotch[2]),(0,255,0),3)
	cv2.imshow("Ukefish", newFrame)

def showUkulele(data,frame):
	frame = cv2.circle(frame,(data.holeSpot),50,(0,255,0),3)
	newSpot = ((data.holeSpot[0] + 100*math.cos(data.rot),
			  (data.holeSpot[1] + 100*math.sin(data.rot))
	frame = cv2.line(frame,(data.holeSpot),(newSpot),(0,255,0),10)
	for finger in data.fingers:
		frame = cv2.circle(frame,(data.holeSpot),20,(0,0,255),3)

	
takeVideo()
