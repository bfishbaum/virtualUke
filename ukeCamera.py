import cv2
import numpy as np
import time
import imgMod
import math
from wavObject import *

WHITE = 255
BLACK = 0
THRESH = 127
TDELTA = 0.2

def sumListTuple(a):
	result = [0 for i in range(len(a[0]))]
	for tuple in a:
		for i in range(len(tuple)):
			result[i] += tuple[i]
	return result

class UkeData(object):
	def __init__(self,corners):
		self.holeSpot = (0,0)
		self.length = 0
		self.rot = 0
		self.fingers = []
		self.strumFinger = (0,0)
		self.strumFingerAbove = False
		self.corners = corners
		self.foundCorners = False
		# strum line is of form y = ax + b
		self.strumLine = (0,0)

		# contains unedited picture of camera input for reuse,
		# never to be edited, only copied from
		self.masterImage = None

		self.fretPoints = []

	#finds the corners, takes in binary image
	def updateCorners(self,frame):
		distance = 5
		size = 10
		dirList = [(x,y) for x in range(-size,size+1) for y in range(-size,size+1)]
		for i in range(len(self.corners)):
			avgX = 0
			avgY = 0
			counter = 0
			for dir in dirList:
				xPos = self.corners[i][1] + distance * dir[0]
				yPos = self.corners[i][0] + distance * dir[1]
				try:
					if(frame[xPos,yPos] == 255):
						avgX += xPos
						avgY += yPos
						counter += 1
				except:
					pass
			if(counter != 0):
				self.corners[i] = (int(avgY/counter),int(avgX/counter))
		self.updateStrumLine()


	def showUkulele(self,frame):
		frame = cv2.cvtColor(frame,cv2.COLOR_GRAY2BGR)
		frame = cv2.circle(frame,(self.holeSpot),50,(0,255,0),3)
		x1 = 20
		strum1 = (x1,int(self.strumLine[0]*x1+self.strumLine[1]))
		x2 = frame.shape[1]-x1
		strum2 = (x2,int(self.strumLine[0]*x2+self.strumLine[1]))
		frame = cv2.line(frame,strum1,strum2,(255,255,0),3)
		for corner in self.corners:
			frame = cv2.circle(frame,(corner),20,(255,0,0),3)
		for point in self.fretPoints:
			frame = cv2.circle(frame,(point),14,(0,255,255),3)
		self.updateFingers(frame)
		return frame

	def updateStrumLine(self):
		result = [0,0]
		corners = sorted(self.corners,key=lambda x: x[0])
		left  = corners[:2]
		right = corners[2:]
		self.updateFretPoints(left,right)
		left  = (int((left[0][0] + left[1][0])/2), int((left[0][1] + left[1][1])/2))
		right = (int((right[0][0]+ right[1][0])/2),int((right[0][1]+ right[1][1])/2))
		# prevent the line from being vertical
		if(right[1] != left[1]):
			result[0] = (right[1]-left[1])/(right[0]-left[0])
		else:
			result[0] = (right[1]-left[1])/(1)
		result[1] = int(left[1]-(result[0]*left[0]))
		self.strumLine = result
	
	def checkForStrum(self):
		above = False
		strumY = self.strumFinger[1] * self.strumLine[0] + self.strumLine[1]
		above = (strumY >= self.strumFinger[1])
		if(above != self.strumFingerAbove):
			self.strumFingerAbove = above
			self.strummed()
		
	def updateFingers(self,frame):
		cols = [x[0] for x in self.corners]
		rows = [x[1] for x in self.corners]
		maxCol = max(cols)
		minCol = min(cols)
		maxRow = max(rows)
		minRow = min(rows)
		fretBoard = self.masterImage[minRow:maxRow, minCol:maxCol]
		fretBoard = imgMod.blackMask(fretBoard) 
	
	def updateFretPoints(self,left,right):
		l1,l2 = left[0],left[1]
		lDX = l2[0]-l1[0]
		lDY = l2[1]-l1[1]
		r1,r2 = right[0],right[1]
		rDX = r2[0]-r1[0]
		rDY = r2[1]-r1[1]
		lPoints = [(int(l1[0] + lDX * x/8), int(l1[1] + lDY * x/8)) for x in range(1,8,2)]
		lPoints.sort(key = lambda x: x[1])
		rPoints = [(int(r1[0] + rDX * x/8), int(r1[1] + rDY * x/8)) for x in range(1,8,2)]
		rPoints.sort(key = lambda x: x[1])
		fretLines = [(lPoints[x],rPoints[x]) for x in range(4)]
		fretPoints = []
		for points in fretLines:
			p1,p2 = points[0], points[1]
			pDX = p2[0]-p1[0]
			pDY = p2[1]-p1[1]
			frets = [(int(p1[0] + pDX * x/8), int(p1[1] + pDY * x/8)) for x in range(1,8,2)]
			frets.sort(key = lambda x: x[0])
			fretPoints += [frets]
		self.fretPoints = fretPoints
	
	def checkFretPoints(self):
		fretBoard = imgMod.blackMask(self.masterImage)
		chordString = ""
		for ukeString in self.fretPoints:
			stringDown = False
			for i in range(len(ukeString)):
				point = ukeString[i]
				if(fretBoard[point[1],point[0]] == 1):
					chordString += str(i)
					stringDown = True
					break
			if(not stringDown):
				chordString += "0"
		return chordString			

def takeVideo():
	cam_index = 0
	cap = cv2.VideoCapture(cam_index)
	found = False
	ukulele = UkeData([(0,0) for x in range(4)])
	time.sleep(1)
	while(True):
		startTime = time.process_time()

		findUkulele(cap,ukulele)

		endTime = time.process_time()
		time.sleep(max(0,0.04 + startTime - endTime))
		if(cv2.waitKey(10) == 27):
			break
	cap.release()
	cv2.destroyAllWindows()

def findUkulele(cap,uke):
	ret, frame = cap.read()
	uke.masterImage = frame
	greenMask = imgMod.greenMask(frame)
	greenMask = imgMod.erode(greenMask,8)
	greenMask = imgMod.dilate(greenMask,12)
	if(not uke.foundCorners):
		blotchArray = imgMod.findBlotches(greenMask,8)
		if(len(blotchArray) == 4):
			uke.corners = [(b[0],b[1]) for b in blotchArray]
			uke.foundCorners = True
	else:
		uke.updateCorners(greenMask)
		greenMask = uke.showUkulele(greenMask)
	cv2.imshow("Uke",greenMask)

takeVideo()
