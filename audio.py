import pyaudio
import wave
import sys
import time
import math
import numpy

LENGTH = 120
BITRATE = 16000
VOLUME = 0.1

class Stream(object):
	def __init__(self):
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format = 8,
						channels = 2,
						rate = 44100,
						output = True)
		self.length = 1024
		self.dataArray = []

	def addFile(self, file):
		wf = wave.open("chords/" + file + ".wav")
		self.dataArray += [wf]
	
	def play(self):
		mix = self.combineArray()
		self.stream.write(mix)
		
	def clear(self):
		self.dataArray = []
		self.stream.stop_stream()

	def close(self):
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()

	def combineArray(self):
		mix = numpy.fromstring("",numpy.int8)
		indices = []
		count = -1
		for note in self.dataArray:
			count += 1
			data = note.readframes(self.length)
			if(data == ""):
				indices += [count]
			decode = numpy.fromstring(data,numpy.int8)
			mix = (decode / len(self.dataArray)).astype(numpy.int8)
		
		# removes finished sounds from array
		for index in indices[::-1]:
			self.dataArray.pop(index)

		return mix
		
stream = Stream()
stream.addFile("chordC")
counter = 0
while True:
	counter += 1
	time.sleep(0.01)
	stream.play()
	print(counter)
	if(counter == 60):
		stream.addFile("chordG")
	elif(counter >= 200):
		break
stream.close()
