import pyaudio
import wave
import sys
import time
import math
import numpy
from multiprocessing import Process

LENGTH = 120
BITRATE = 16000
VOLUME = 0.1

class WAV(object):
	def __init__(self,file):
		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format = 8,
						channels = 2,
						rate = 44100,
						output = True)
		self.length = 10240
		self.wf = wave.open("chords/" + file + ".wav")
	
	def play(self):
		data = self.wf.readframes(self.length)
		if(data == b''):
			return False
		self.stream.write(data)
		data = self.wf.readframes(self.length)
		return True
		
	def close(self):
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()

	def __del__(self):
		self.close()
