# made to test using pyaudio
import pyaudio
from array import array
import time
import wave
import sys
from tkinter import *
import copy

FORMAT      =    pyaudio.paInt16
RATE        =    48000
CHANNELS    =    1
CHUNK_SIZE  =    1024

def timerFired(data):
	data.audioChunk = list(data.stream.read(1024,False))
	data.record.append(data.audioChunk)
	for x in range(len(data.audioChunk)):
		data.audioChunk[x] += 128
		data.audioChunk[x] %= 256
	i = 0
	x = 0
	while(x < len(data.audioChunk)):
		if(abs(data.audioChunk[x]-128) < 0):
			data.audioChunk.pop(x)
		else:
			x += 1

def init(data):
	data.audioChunk = []
	data.hz = 0
	data.hzList = []
	# 1 FPS
	data.timerDelay = 1
	
	# initalizes the pyaudio and the audio stream
	data.audio = pyaudio.PyAudio()
	data.stream = data.audio.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
				input = True,
                output = False,
				frames_per_buffer = CHUNK_SIZE)

def mousePressed(event,data):
	if(pointInRect(event.x,event.y,(10,290,295,590))):
		buttonOne(data)
	elif(pointInRect(event.x,event.y,(310,290,595,590))):
		buttonTwo(data)
		
def buttonOne(data):
	data.hz = 100

def buttonTwo(data):
	data.hz = 200

def pointInRect(x,y,rect):
	if(x < rect[0]):   return False
	elif(x > rect[2]): return False
	elif(y < rect[1]): return False
	elif(y > rect[3]): return False
	return True

def findHz(chunk):
	periods = 0
	for i in range(1, len(chunk) - 1):
		if(abs(chunk[i]) > abs(chunk[i-1]) and abs(chunk[i]) > abs(chunk[i+1])):
			periods += 1
	return periods

def drawAll(canvas,data):
	canvas.create_rectangle(10,290,295,590,fill="white")
	canvas.create_rectangle(310,290,595,590,fill="white")
	for x in range(len(data.audioChunk)-1):
		point1 = (x-1, 280-data.audioChunk[x-1])
		point2 = (  x,280-data.audioChunk[x])
		canvas.create_line(point1,point2,fill="black")
	canvas.create_text(300,100,text = str(data.hz),font="Arial 50")
	
def run():
	def mousePressedWrapper(event,canvas,data):
		mousePressed(event,data)		
		redrawAllWrapper(canvas, data)
	def redrawAllWrapper(canvas, data):
		canvas.delete(ALL)
		drawAll(canvas,data)
		canvas.update()
	def timerFiredWrapper(canvas, data):
		timerFired(data)
		redrawAllWrapper(canvas, data)
		# pause, then call timerFired again
		canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
	root = Tk()
	canvas = Canvas(root,width=600,height=600)
	canvas.pack()
	class Struct(object): pass
	data = Struct()
	init(data)
	root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
	redrawAllWrapper(canvas, data)
	timerFiredWrapper(canvas,data)
	root.mainloop()
	data.audio.terminate()

run()
