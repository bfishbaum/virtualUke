import cv2
import numpy as np
import time
import imgMod
import math
import mathFuncs
import wavObject


class FakeUke(object):
	def __init__(self,corners):
		self.fingers = []
		self.strumFinger = (0,0)
		self.strumFingerAbove = None
		self.corners = corners
		self.foundCorners = False
		self.foundStrumFinger = False
		# strum line is of form y = ax + b
		self.strumLine = (0,0)
		self.soundObject = None
		# contains unedited picture of camera input for reuse,
		# never to be edited, only copied from
		self.masterImage = None

		self.fretPoints = []

		# for testing purposes
		self.currentChord = "C"

	#finds the corners, takes in binary image
	def updateCorners(self,frame):
		if(self.foundCorners):
			cornersSeen = 0
			distance = 5
			size = 10
			dirList = [(x*distance,y*distance) for x in range(-size,size+1) for y in range(-size,size+1)]
			for i in range(len(self.corners)):
				newPoint = imgMod.avgLocOfSurrounding(frame,self.corners[i],dirList)
				if(newPoint != None):
					self.corners[i] = newPoint
					cornersSeen += 1
			if(cornersSeen == 0):
				self.foundCorners = False	
			else:
				self.updateStrumLine()
		else:
			blotchArray = imgMod.findBlotches(frame,10)
			if(len(blotchArray) == 4):
				self.corners = [(b[0],b[1]) for b in blotchArray]
				self.foundCorners = True

	def updateStrumLine(self):
		result = [0,0]
		corners = sorted(self.corners,key=lambda x: x[0])
		left  = corners[:2]
		right = corners[2:]
		self.updateFretPoints(left,right)
		left  = (int((left[0][0] + left[1][0])/2), int((left[0][1] + left[1][1])/2))
		right = (int((right[0][0]+ right[1][0])/2),int((right[0][1]+ right[1][1])/2))
		# prevent the line from being vertical
		if(right[0] != left[0]):
			result[0] = (right[1]-left[1])/(right[0]-left[0])
		else:
			result[0] = (right[1]-left[1])/(1)
		result[1] = int(left[1]-(result[0]*left[0]))
		self.strumLine = result

	def updateStrumFinger(self,frame):
		blotchArray = imgMod.findBlotches(frame,10)
		if(len(blotchArray) >= 1):
			biggestBlotch = max([x for x in blotchArray],key = lambda x: x[2])
			self.strumFinger = (biggestBlotch[0],biggestBlotch[1])
		self.checkForStrum()
		
	def checkForStrum(self):
		above = False
		strumY = self.strumFinger[0] * self.strumLine[0] + self.strumLine[1]
		above = strumY >= self.strumFinger[1]
		if(not above and self.strumFingerAbove == True):
			self.strummed()
		self.strumFingerAbove = above
		
	def strummed(self):
		chordString = self.checkChordLines()
		if(chordString != None):
			self.currentChord = chordString
#			self.soundObject = wavObject.WAV("chord" + chordString)
			sound = wavObject.WAV("chord" + chordString)
			sound.play()

			

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
		_,fretBoard = self.getFretBoard()
		fretBoard = imgMod.blueMask(fretBoard)
		fretBoard = imgMod.dilate(fretBoard,5)
		# chord string refers to 4 numbers representing
		# the fingers' positions on the strings
		chordString = ""
		# uke string refers to each string on the ukulele,
		# not a string of characters
		for ukeString in self.fretPoints:
			stringDown = False
			for i in range(len(ukeString)):
				point = ukeString[i]
				if(self.checkFretForFinger(point,fretBoard)):
					chordString += str(i+1)
					stringDown = True
					break
			if(not stringDown):
				chordString += "0"
		return chordString			

	def checkFretForFinger(self,point,img):
		# checks five pixel square
		distance = 1
		dirList = [(x*distance+point[0],y*distance+point[1]) for x in range(-size,size+1) for y in range(-size,size+1)]
		for dir in dirList:
			try:
				if(img[dir[1],dir[0]] == 255):
					return True
			except: pass
		return False

	def checkChordLines(self):
		# makes sure board is ok, and there is a blotch
		try:
			rect, fretBoard = self.getFretBoard()
			fretBoard = imgMod.blueMask(fretBoard)
			fretBoard = imgMod.dilate(imgMod.erode(fretBoard,5),10)
		except:
			return None
		try:
			blotch = max(imgMod.findBlotches(fretBoard,10),key = lambda x: x[2])
		except:
			return None
		
		# this function finds the largest blotch
		# and finds where it is located horizontally
		# on the fret board

		finger = (blotch[0]+rect[0],blotch[1]+rect[2])
		self.fingers = [finger]
		rightCorners = sorted(self.corners,key=lambda x:x[0])[:2]

		area = mathFuncs.herosFormula(finger,rightCorners[0],rightCorners[1])
		try:
			altitude = 2*(area/mathFuncs.distance(rightCorners[0],rightCorners[1]))
		except:
			altitude = 100

		topCorners = sorted(self.corners,key=lambda x:x[1])[:2]
		fretLength = mathFuncs.distance(topCorners[0],topCorners[1])
		try:
			xPosNorm = altitude/fretLength
		except:
			return None

		if(xPosNorm < 0.25):
			return "A"
		elif(xPosNorm < 0.5):
			return "F"
		elif(xPosNorm < 0.75):
			return "C"
		elif(xPosNorm < 1):
			return "G"
		
	
	# returns the slice of the master image
	# that corresponds to the fretboard
	def getFretBoard(self):
		maxX = max(self.corners, key = lambda x: x[0])[0]
		minX = min(self.corners, key = lambda x: x[0])[0]
		maxY = max(self.corners, key = lambda x: x[1])[1]
		minY = min(self.corners, key = lambda x: x[1])[1]
		try: 
			return (minX,maxX,minY,maxY), self.masterImage[minY:maxY,minX:maxX]
		except:
			return None
	

	def showUkulele(self):
		frame = self.masterImage
		x1 = -20
		strum1 = (x1,int(self.strumLine[0]*x1+self.strumLine[1]))
		x2 = frame.shape[1]-x1
		strum2 = (x2,int(self.strumLine[0]*x2+self.strumLine[1]))
		frame = cv2.line(frame,strum1,strum2,(255,255,0),3)

		for corner in self.corners:
			frame = cv2.circle(frame,(corner),20,(255,0,0),3)

#		for line in self.fretPoints:
#			for point in line:
#				frame = cv2.circle(frame,(point),14,(0,255,255),3)

		for finger in self.fingers:
			frame = cv2.circle(frame,(finger),14,(0,255,255),3)

		textMargin = 100
		textFont = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(frame,self.currentChord,(frame.shape[1]-textMargin,textMargin),textFont,4,(255,0,255),2,cv2.LINE_AA)

		frame = cv2.circle(frame,(self.strumFinger),40,(0,0,255),3)

		return frame

	def playSoundObject(self):
		if(self.soundObject != None):
			if(not self.soundObject.play()):
				self.soundObject = None
