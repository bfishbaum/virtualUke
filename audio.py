import pyaudio
import sys
import time
import math

LENGTH = 2
BITRATE = 16000
FREQUENCY = 2000
VOLUME = 0.1

def playBeep():
	data = [int(128*VOLUME) + int(128 * VOLUME * math.sin(x*(BITRATE/FREQUENCY)*math.pi/180)) for x in range(LENGTH*BITRATE)]
	p = pyaudio.PyAudio()
	
	stream = p.open(format = pyaudio.paInt16,
					channels = 1,
					rate = BITRATE,
					output = True)
	
	sound = [chr(i) for i in data]
	stream.write(''.join(sound))
	stream.stop_stream()
	stream.close()
	p.terminate()

playBeep()
