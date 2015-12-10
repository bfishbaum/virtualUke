import cv2
import numpy as np
import time
import imgMod
import math
from mathFuncs import *
import ukeCamera
import pygame
from pygame.locals import *

TDELTA = 0.016

def splashScreen():
	frame = cv2.imread("splashScreen.png",3)
	cv2.imshow("Uke",frame)
	while(True):
		if(cv2.waitKey(10) != -1):
			break
	frame = cv2.imread("instructions.png",3)
	cv2.imshow("Uke",frame)
	while(True):
		if(cv2.waitKey(10) != -1):
			break
	frame = cv2.imread("loadingScreen.png",3)
	cv2.imshow("Uke",frame)
	

def takeVideo():
	cam_index = 0
	cap = cv2.VideoCapture(cam_index)
	found = False
	ukulele = ukeCamera.FakeUke([(0,0) for x in range(4)])
	time.sleep(1)
	while(True):
		startTime = time.process_time()

		updateUkulele(cap,ukulele)

		endTime = time.process_time()

#		sleepTime = max(0,TDELTA-endTime+startTime)
		if(cv2.waitKey(10) == 27):
			break
	ukulele.cleanUp()
	cap.release()
	cv2.destroyAllWindows()

def updateUkulele(cap,uke):
	# needs to find strumming finger and 4 corners
	ret, frame = cap.read()
	uke.masterImage = frame

	greenMask = imgMod.dilate(imgMod.erode(imgMod.greenMask(frame),8),12)
	redMask = imgMod.dilate(imgMod.erode(imgMod.redMask(frame),33),22)

	uke.updateCorners(greenMask)
	uke.updateStrumFinger(redMask)

	cv2.imshow("Uke",uke.showUkulele())
		
def testRedMask(cap):
	ret, frame = cap.read()
	redMask = imgMod.dilate(imgMod.erode(imgMod.blackMask(frame),3),3)
	cv2.imshow("Uke",redMask)

def startApp():
	splashScreen()
	takeVideo()

startApp()
