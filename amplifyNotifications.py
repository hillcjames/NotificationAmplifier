import subprocess
import time
import os
import numpy
import sys

import textwrap

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import cv2

def main():
	for overheardMessage in execute(['sh', './listenForNotifySend.sh']):
		#print("original msg: " + overheardMessage)
		line = time.strftime('%l:%M%p %Z on %b %d, %Y') + ":\t" + overheardMessage
		with open("fullLog.txt", "a") as logFile:	
			logFile.write(line)
		parseNotifySendMessage(overheardMessage)


# from https://stackoverflow.com/questions/4417546
def execute(cmd):
	popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
	for stdout_line in iter(popen.stdout.readline, ""):
    		yield stdout_line 
	popen.stdout.close()
	return_code = popen.wait()
	if return_code:
		raise subprocess.CalledProcessError(return_code, cmd)



notificationNoticed = False
message = ""

'''
notify-send sends messages that look like the below. Remember each line must be processed on its own. I would like to use pcregrep, except I can't get it to work with dbus output for some reason.

method call time=1544635353.210271 sender=:1.17581 -> destination=:1.25 serial=6 path=/org/freedesktop/Notifications; interface=org.freedesktop.Notifications; member=GetServerInformation
method call time=1544635353.222796 sender=:1.17581 -> destination=:1.25 serial=7 path=/org/freedesktop/Notifications; interface=org.freedesktop.Notifications; member=Notify
   string "notify-send"
   uint32 0
   string "Title"
   string "something"
   string " Body
	Body second line
	Body third line"
   array [
   ]
   array [
      dict entry(
         string "urgency"
         variant             byte 1
      )
   ]
   int32 -1

'''
def parseNotifySendMessage(notifySendTextLine):
	global notificationNoticed
	global message
	line = notifySendTextLine.strip()
	words = line.split()

	if len(words) == 0:
		return

	if (words[0] == 'method'): # start of notification message section
		notificationNoticed = True
		message = ""
		return

	if (not notificationNoticed): # ignore any lines outside of the notification section
		return

	if (words[0] == 'array'): # end of notification message section
		notificationNoticed = False
		if message[-1:] == "\n":
			message = message[:-1]
		logNotification(message)
		showNotification(message)
		return

	if (words[0][:4] == "uint"): # ignore the declartion of the encoding - hopefully its some type of unit*
		return

	else: # the line is part of the message. It may or may not start with "string ", but if it does, remove that.
		# it probably will contain some number of double-quotes; parse around those.
		payload = line.split("\"")
		if payload[0] == "string ":
			payload = payload[1:] # remove the starting "string "
		
		for section in payload:
			if section != "":
				message += section + "\n"
	
		return

	print("you shouldn't be here - line was " + line)
		

def logNotification(msg):
	msg = msg.replace("\n", ":\\n:")

	line = time.strftime('%l:%M%p %Z on %b %d, %Y') + ", [message]" + msg + "[/message]\n"

	print(line)
	with open("notificationLog.txt", "a") as logFile:	
		logFile.write(line)


def showNotification(msg):

	secondsShown = 5
	backgroundColor = (70,0,50)
	pilImg = Image.new("RGBA", (300,200), backgroundColor)
	toDraw = []
	draw = ImageDraw.Draw(pilImg)
	# or whatever font file you have on your system and would like to use.
	font = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf", 32)

	class TextLine:
		def __init__(self, width, yOffset, text):
			self.width = width
			self.yOffset = yOffset
			self.text = text

	margin = 40
	yOffset = margin
	maxCharsPerLine = 30
	maxW = 0
	for section in msg.split("\n"):
		for line in textwrap.wrap(section, width=maxCharsPerLine):
			wT, hT = font.getsize(line)

			toDraw.append(TextLine( wT, yOffset, line))

			yOffset += hT
			if maxW < wT:
				maxW = wT

		yOffset += margin

	if yOffset + margin > pilImg.height or maxW + 2*margin > pilImg.width:
		pilImg = Image.new("RGBA", (maxW + 2*margin, yOffset + margin), backgroundColor)
		draw = ImageDraw.Draw(pilImg)
	

	for lineOfText in toDraw:
		coords = ((pilImg.width - lineOfText.width)/2, lineOfText.yOffset)
		draw.text(coords, lineOfText.text, font=font, fill="#fff")


	tempArray = numpy.array(pilImg)
	cvImg = tempArray[:, :].copy()


	# window name must be reliably unique, among any other window that you may have open.
	winName = '/__Notification__/'

	#https://stackoverflow.com/questions/49095446/python-opencv-remove-title-bar-toolbar-and-status-bar
	cv2.imshow(winName, cvImg)
	cv2.namedWindow(winName, cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty(winName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

	activeWindowID = subprocess.check_output(["xdotool", "getactivewindow"]).replace("\n", "")
	time.sleep(0.5)	 # wait a sec 
	cv2.waitKey(200) # wait for window to load

	#https://stackoverflow.com/questions/21277738
	# bring window to front, in case it isn't already
	subprocess.check_output(["wmctrl", "-a", winName])

	# but keep the old window active, so if it pops up while you're typing, it doesn't steal your keypresses
	# (esp. so it doesn't immediately close)
	try:
		subprocess.check_output(["xdotool", "windowfocus", activeWindowID])
	except:
		print("Could give focus back to original window; too many notiifcations at once. This could use a queue of some sort.")


	cv2.waitKey(1000 * secondsShown)
	cv2.destroyWindow(winName)


if __name__ == "__main__":
	main()



