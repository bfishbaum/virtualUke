import pyaudio
import cv2
import numpy
import math
import time

def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def findChordFile(chord):
	chords = readFile("chordList").splitlines()
	for i in chords:
		if(i.startswith(chord)):
			return "chord" + i.split()[-1] + ".wav"


# boardRect is a list of 4 points
# representing the edges of board
# being held to represent the uke

def findDownLocale(boardRect,fingerPoints):
	# convert global positional data to
	# positional data local to the board
	topLeft = boardRect[0]
	topRight = boardRect[1]
	bottomLeft = boardRect[2]
	bottomRight = boardRect[3]

	(vX,vY) = (topRight[0]-topLeft[0],topRight[1]-topLeft[1])
	(wX,wy) = (bottomLeft[0]-topLeft[0],bottomLeft[1]-topLeft[1])

	fingerVectors = []
	for x in fingerPoints:
		dX = x[0]-topLeft[0]
		dY = x[1]-topLeft[1]

		# dX = a*vX + b*wX
		# dY = a*vY + b*wY	
		
		a = (dY*wX-dX*wY)/(wX*vY-wY*vX)
		b = (dX - a*vX)/wX
		fingerVectors.append((a,b))	
	
	#returns normalized location of fingers in boardRect
	return fingerVectors
	
def findDownFrets(fingerVectors):
	# convert positional data to fret data
	frets = []
	for loc in fingerVectors:
		fretString = ""
		if(not (loc[0] < 0 or loc[0] > 1 or loc[1] < 0 or loc[1] > 1)):
			if(loc[1] < 0.25):		fretString = "G"
			elif(loc[1] < 0.5):		fretString = "C"
			elif(loc[1] < 0.75):    fretString = "A"
			else:					fretString = "E"

			if(loc[0] > 0.9):		fretString += "9"
			elif(loc[0] > 0.8):		fretString += "8"
			elif(loc[0] > 0.7):		fretString += "7"
			elif(loc[0] > 0.6):		fretString += "6"
			elif(loc[0] > 0.5):		fretString += "5"
			elif(loc[0] > 0.4):		fretString += "4"
			elif(loc[0] > 0.3): 	fretString += "3"
			elif(loc[0] > 0.2):		fretString += "2"
			elif(loc[0] > 0.1):		fretString += "1"
			else:					fretString += "0"
	
			frets += [fretString]
	return(sorted(frets))

def fretsToChord(frets):
	g,c,e,a = 0,0,0,0
	for fret in frets:
		if(fret.startswith("A")):
			a = int(fret[1:])
		elif(fret.startswith("C")):
			c = int(fret[1:])
		elif(fret.startswith("F")):
			f = int(fret[1:])
		elif(fret.startswith("G")):
			g = int(fret[1:])

	chord = str(g) + str(c) + str(e) + str(a)
	
