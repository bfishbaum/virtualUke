import cv2
import numpy as np
import time
import imgMod
import math
from mathFuncs import *
import ukeCamera

def readFile(path):
	with open(path,"rt") as f:
		return f.read()

WHITE = 255
BLACK = 0
THRESH = 127
TDELTA = 0.2

def takeVideo():
	cam_index = 0
	cap = cv2.VideoCapture(cam_index)
	found = False
	ukulele = ukeCamera.FakeUke([(0,0) for x in range(4)])
	time.sleep(1)
	while(True):
		startTime = time.process_time()

		updateUkulele(cap,ukulele)
#		testRedMask(cap)

		endTime = time.process_time()

		if(cv2.waitKey(10) == 27):
			break
	cap.release()
	cv2.destroyAllWindows()


def updateUkulele(cap,uke):
	# needs to find strumming finger and 4 corners
	ret, frame = cap.read()

	uke.masterImage = frame

	greenMask = imgMod.dilate(imgMod.erode(imgMod.greenMask(frame),8),12)
	redMask = imgMod.dilate(imgMod.erode(imgMod.redMask(frame),33),22)
	time1 = time.clock()
	uke.updateCorners(greenMask)
	time2 = time.clock()
	uke.updateStrumFinger(redMask)
	time3 = time.clock()
	print(time3-time2,time2-time1)
	time1 = time.clock()
	uke.playSoundObject()
	
	cv2.imshow("Uke",uke.showUkulele())
		
def testRedMask(cap):
	ret, frame = cap.read()
	redMask = imgMod.dilate(imgMod.erode(imgMod.blackMask(frame),3),3)
	cv2.imshow("Uke",redMask)

takeVideo()
