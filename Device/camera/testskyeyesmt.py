
# Please use tab's.

from picamera.array import PiRGBArray
from picamera       import PiCamera
import time
import cv2
import sys
import requests

import os
import platform
from os import listdir
from os.path import isfile, join

import threading
import datetime
from time import gmtime,strftime

class Job:
	def __init__(self, file, url):
		self.file = file
	def do(self):
		data = open(self.file , "rb").read()
		res = requests.post( url = url,data = data, headers={"Content-Type": "application/octet-stream"})
		
		
def PostToSkyEyes(*args):
	job = Job(args[0], args[1])
	job.do()

#faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
faceCascade = cv2.CascadeClassifier("data.xml")
cam            = PiCamera()
cam.resolution = (320, 240)
cam.framerate  = 30
raw            = PiRGBArray(cam, size=(320, 240))
count = 0
def createHaarCascade(path):
        files = [f for f in listdir(path) if isfile(join(path, f))]
        hash = ""
        for file in files:
		if file.endswith(".xml"):
	                stat = os.stat(file)
        	        try:
                	        hash = hash + "|" + ("{0}-{1}".format(file , stat.st_birthtime))
	                except AttributeError:
        	                # We're probably on Linux. No easy way to get creation dates here, so we'll
                	        # settle for when its content was last modified.
                        	hash = hash + "|" + ("{0}-{1}".format(file , stat.st_mtime))
        

hash = createHaarCascade("./")
url = "https://prod-10.northcentralus.logic.azure.com/workflows/<your flow id>/triggers/manual/paths/invoke/devices/{0}/localtime/{1}?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=FIBdMSXq9TAgfrnKEXf33e8is62Y9mzNmAxVFdmjKnQ"
time.sleep(0.1) # Camera warm up
prevDetected = 0

for frameBGR in cam.capture_continuous(raw, format="bgr", use_video_port=True):
	imgBGR = frameBGR.array # num.py array
	imgBW  = cv2.cvtColor(imgBGR, cv2.COLOR_BGR2GRAY)


        listFace = faceCascade.detectMultiScale(
		imgBW,
		scaleFactor=1.1,
		minNeighbors=5,
		minSize=(30, 30),
		#flags=cv2.cv.CV_HAAR_SCALE_IMAGE
		#v3.1+
		flags=cv2.CASCADE_SCALE_IMAGE
        )
	
	if len(listFace) > 0 and (len(listFace) != prevDetected):
		print("len(listFace)={0}/prevDetected={1}".format(len(listFace),prevDetected))
		
	        #write image to file
        	cv2.imwrite("./test%d.jpg" % count , imgBGR)
	        print ("writing file")
        	
		#read file and send to cloud
		thread = threading.Thread(target=PostToSkyEyes, name="post", args=("./test{0}.jpg".format(count),url.format("test001", strftime("%Y%m%d%H%M%S",gmtime())),))
		thread.start()

		#data = open("./test%d.jpg" % count, "rb").read()
		#res = requests.post( url = url,data = data, headers={"Content-Type": "application/octet-stream"})
		print ("done posting")
	        count = count + 1

	prevDetected = len(listFace)

        for (x, y, w, h) in listFace:
		cv2.rectangle(imgBGR, (x, y), (x+w, y+h), (255, 255, 0), 4)

	print len(listFace)
	cv2.imshow('Video', imgBGR)

	key = cv2.waitKey(1) & 0xFF
 
	raw.truncate(0) # Clear stream, a must!
 
	if key == ord("q"): # Press 'q' to quit
		break
	if key == ord("t"): # Press 'q' to quit
		hash = ""
		
	newHash = createHaarCascade("./")
	if (hash == newHash) == False:
		faceCascade = cv2.CascadeClassifier("data.xml")
		hash = newHash
		prevDetected = 0
		print("loading new cascade classifier......................................")


