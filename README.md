
This was created to supplement, in a fairly hacky and crude way, the (currently unfixed) failings of notify-send on ubuntu 18.04.
On that platform, notify-send only displays on your primary monitor (not necessarily the active monitor), notifications are not logged, and there's very little you can customize. This solves the first two problems, and provides a framework to address the other.
There are more elegant solutions (e.g. clones of notify-send), but I made this because python's quick to write in, and so anyone else will be able to quickly peruse the code and see that it doesn't have any hidden/malicious actions - something which I personally don't trust myself to find in a larger package.


It listens for calls to notify-send (without intercepting them), and prints out the call's message on an image. The image will (should) popup on whatever screen is active, and close itself after 5 seconds. All notification messages are logged in a text file in the folder from which the python script is run. 


Prereqs:

	pip install opencv-python
	pip install Pillow
	sudo apt-get install wmctrl
	sudo apt-get install xdotool

to use, just leave it running in the background:

`python ./amplifyNotifications.py`
