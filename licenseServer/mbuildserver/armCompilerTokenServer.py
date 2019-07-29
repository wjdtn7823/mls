import serverInterface
import os
import signal

def sighandler(signal,frame):
	print ("server closing")
	os._exit(0)

if __name__ == "__main__":
	s=serverInterface.LicenseServer()
	s.start()	
	signal.signal(signal.SIGINT,sighandler)
	signal.pause()
