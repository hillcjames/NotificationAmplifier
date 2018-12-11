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



def parseNotifySendMessage(notifySendTextLine):
	# all lines of text will have the form `  string "message"`
	message = notifySendTextLine.strip().split("\"")[1]

	if (message != "notify-send" and message != "urgency" 
	    and message != "" and message[:3] != ":1."):
		logNotification(message)
		showNotification(message)
	

def logNotification(msg):
	line = time.strftime('%l:%M%p %Z on %b %d, %Y') + ", [message]:\t" + msg + "[/message]\n"

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
	font = ImageFont.truetype("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf", 40)

	class TextLine:
		def __init__(self, width, yOffset, text):
			self.width = width
			self.yOffset = yOffset
			self.text = text

	margin = 40
	yOffset = margin
	maxCharsPerLine = 30
	maxW = 0
	for line in textwrap.wrap(msg, width=maxCharsPerLine):
		wT, hT = font.getsize(line)

		toDraw.append(TextLine( wT, yOffset, line))

		yOffset += hT
		if maxW < wT:
			maxW = wT


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

	cv2.namedWindow(winName)
	cv2.imshow(winName, cvImg)
	activeWindowID = subprocess.check_output(["xdotool", "getactivewindow"])
	time.sleep(0.5)	 # wait a sec 
	cv2.waitKey(200) # wait for window to load

	#https://stackoverflow.com/questions/21277738
	# bring window to front, in case it isn't already
	subprocess.check_output(["wmctrl", "-a", winName])

	# but keep the old window active, so if it pops up while you're typing, it doesn't steal your keypresses
	# (esp. so it doesn't immediately close)
	subprocess.check_output(["xdotool", "windowfocus", activeWindowID])


	cv2.waitKey(1000 * secondsShown)
	cv2.destroyWindow(winName)


if __name__ == "__main__":
	main()



