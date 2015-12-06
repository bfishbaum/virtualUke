import cv2
import numpy as np

WHITE = 255
BLACK = 0
THRESH = 127

def cropImage(frame,sizeX,sizeY):
	size = frame.shape
	y1 = (size[0] - sizeX)//2
	y2 = x1 + sizeX
	x1 = (size[1] - sizeY)//2
	x2 = y1 + sizeY
	return frame[y1:y2,x1:x2]

def redMask(frame):
	min1 = np.uint8([[0,50,50]])
	max1 = np.uint8([[10,255,255]])
	min2 = np.uint8([[170,50,50]])
	max2 = np.uint8([[180,255,255]])

	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

	return cv2.add(cv2.inRange(hsv,min1,max1), cv2.inRange(hsv,min2,max2))

def greenMask(frame):
	min = np.uint8([[ 40, 50, 50]])
	max = np.uint8([[ 60,255,255]])
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

	return cv2.inRange(hsv,min,max)

def blackMask(frame):
	min = np.uint8([[  0,  0,  0]])
	max = np.uint8([[180,255, 25]])
		
	return cv2.inRange(frame,min,max)


def balsaWoodMask(frame):
	min = np.uint8([[0,0,160]])
	max = np.uint8([[160,20,200]])
	hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
	return cv2.inRange(hsv,min,max)

	

def erode(image,strength):
	return cv2.erode(image,np.ones((strength,strength), np.uint8))

def dilate(image,strength):
	return cv2.dilate(image,np.ones((strength,strength), np.uint8))

def open(image, strength):
	return(dilate(erode(image, strength), strength))

def close(image, strength):
	return(erode(dilate(image, strength), strength))

def binary(image):
	imgray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	ret,thresh = cv2.threshold(imgray,127,255,0)
	return thresh

def blur(image, strength):
	return cv2.GaussianBlur(image,(strength*2 + 1,strength*2 + 1),5)

# find the centers of all the blotches 
# requires image to be binary
# accuracy is int, lower is more accurate, min at one
	
def findBlotches(image,accuracy):
	pointSet = set()
	size = image.shape

	def floodFillPoints(x,y):
		if(x < 0 or x >= size[1] or y < 0 or y >= size[0]):
			return []
		if((y,x) in pointSet):
			return []
		else:
			pointSet.add((y,x))
		if(image[y,x] == 255):
			temp1 = floodFillPoints(x+accuracy,y)
			temp2 = floodFillPoints(x-accuracy,y)
			temp3 = floodFillPoints(x,y-accuracy)
			temp4 = floodFillPoints(x,y+accuracy)
			return [(x,y)] + temp1 + temp2 + temp3 + temp4
		else:
			return []
	
	blotchArrays = []	
	for x in range(0,size[1],accuracy):
		for y in range(0,size[0],accuracy):
			blotch = floodFillPoints(x,y)
			if(blotch != []):
				blotchArrays += [blotch]

	avgArray = []
	for blotch in blotchArrays:
		avgX = 0
		avgY = 0
		for point in blotch:
			avgX += point[1]
			avgY += point[0]
		avgX = int(avgX / len(blotch))
		avgY = int(avgY / len(blotch))
		avgArray += [[avgY,avgX,(len(blotch)*accuracy)**0.5]]
	
	return avgArray
	
