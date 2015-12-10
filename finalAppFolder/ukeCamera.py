import cv2
import numpy as np
import time
import imgMod
import math
import mathFuncs
import wavObject
import pygame


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
		pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
		self.fretPoints = []

		# for testing purposes
		self.currentChord = "C"

	#finds the corners, takes in binary image
	def updateCorners(self,frame):
		if(self.foundCorners):
			cornersSeen = 0
			distance = 8
			size = 10
			dirList = [(x*distance,y*distance) for x in range(-size,size+1) for y in range(-size,size+1)]
			for i in range(len(self.corners)):
				newPoint = imgMod.avgLocOfSurrounding(frame,self.corners[i],dirList)
				if(newPoint != None):
					self.corners[i] = newPoint
					cornersSeen += 1
			if(cornersSeen <= 2):
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
		if(self.foundStrumFinger):
			distance = 12
			size = 10
			dirList = [(x*distance,y*distance) for x in range(-size,size+1) for y in range(-size,size+1)]
			newPoint = imgMod.avgLocOfSurrounding(frame,self.strumFinger,dirList)
			if(newPoint != None):
				self.strumFinger = newPoint
			else:
				self.strumFinger = (0,0)
				self.foundStrumFinger = False
				self.strumFingerAbove = None
			
			if(self.foundCorners):
				self.checkForStrum()
		else:
			blotchArray = imgMod.findBlotches(frame,10)
			if(len(blotchArray) >= 1):
				biggestBlotch = max([x for x in blotchArray],key = lambda x: x[2])
				self.strumFinger = (biggestBlotch[0],biggestBlotch[1])
				self.foundStrumFinger = True
		
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
			chord = pygame.mixer.Sound("chords/chord" + chordString + ".wav")
			chord.play()

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
		# y,x, channels
		size = frame.shape
		textFont = cv2.FONT_HERSHEY_SIMPLEX
		backgroundColor = (255,255,255)

		if(self.foundCorners):
			for corner in self.corners:
				frame = cv2.circle(frame,(corner),20,(255,0,0),3)
			x1 = -20
			strum1 = (x1,int(self.strumLine[0]*x1+self.strumLine[1]))
			x2 = frame.shape[1]-x1
			strum2 = (x2,int(self.strumLine[0]*x2+self.strumLine[1]))
			frame = cv2.line(frame,strum1,strum2,(255,255,0),3)
		else:
			fontSize = 1.5
			textColor = (0,0,0)
			frame = cv2.rectangle(frame,(size[1]//2-150,size[0]//2+50),(size[1]//2+150,size[0]//2-50),backgroundColor,-1)
			imgMod.putTextCenter(frame,"Corners",(size[1]//2,size[0]//2),textFont,fontSize,textColor,2,cv2.LINE_AA)
			imgMod.putTextCenter(frame,"Not Found",(size[1]//2,size[0]//2+50),textFont,fontSize,textColor,2,cv2.LINE_AA)

		for finger in self.fingers:
			frame = cv2.circle(frame,(finger),14,(0,255,255),3)

		textMargin = 100
		frame = cv2.rectangle(frame,(size[1]-textMargin,0),(size[1],textMargin),backgroundColor,-1)
		imgMod.putTextCenter(frame,self.currentChord,(size[1]-textMargin//2,textMargin//2+50),textFont,2,(255,0,255),2,cv2.LINE_AA)

		frame = cv2.circle(frame,(self.strumFinger),40,(0,0,255),3)

		return frame

	def playSoundObject(self):
		if(self.soundObject != None):
			if(not self.soundObject.play()):
				self.soundObject = None

	def cleanUp(self):
		pygame.mixer.quit()

