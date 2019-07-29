import time
import threading
import socket
import os
import subprocess
import time
import logging
import signal

exit=False
buffSize=1024


def LogHandler():
    logger=logging.getLogger('licenseClient')
    fileHandler=logging.FileHandler('build/licenseClient.log')
    streamHandler=logging.StreamHandler()
   
    formatter=logging.Formatter('[%(levelname)s|%(filename)s.%(lineno)d] %(asctime)s >>> %(message)s]')
   
    fileHandler.setFormatter(formatter);
    streamHandler.setFormatter(formatter);
    
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.DEBUG);
   
    return logger

logger=LogHandler()

class SignalHandler():
	def __init__(self):
		try:
			self.pid=subprocess.check_output("ps -e | grep mbuild | awk '{print $1}'|head -n 1",shell=True)
		except Exception as e:
			print e	

	def sendStartSignal(self): #this will progress mbuild process
		logger.debug("sendStartSignal to mbuild")
		try :
			os.kill(int(self.pid),signal.SIGUSR2)
		except Exception as e:
			print e
			os._exit(1)

	def sendKillSignal(self): ##this will stop mbuild process.
		logger.debug("sendKILLSignal to mbuild")
		try :
			os.kill(int(self.pid),signal.SIGUSR1)
		except Exception as e:
			print e
			os._exit(1)

class clientThread(threading.Thread):

	def __init__(self,conn):
		self.conn=conn		
		self.sg=SignalHandler()
		threading.Thread.__init__(self)
		self.status="INITT"
		self.Mo=MyMonitor()
		self.retry=0

	def __del__(self):
		self.conn.close()

	def run(self):
		logger.debug("Client status to (INIT)")
		while self.status!="ERROR" and exit == False :
			status=self.status
			func=getattr(self,status[:5].strip())
			func()
			time.sleep(1)
		logger.debug("CLEANING Thread resource")
		self.CLEAN()
		return

	def INITT(self):
		try:
			self.conn.send("INITT")
		except Exception as e:
			self.status="ERROR"
			logger.debug("Client error at INITT")
			return

		try:
			rsp=self.conn.recv(buffSize)
		except Exception as e:
			self.status="ERROR"
			logger.debug("Client error at INITT recv")
			return
		if rsp=="START":
			self.status="START"
			logger.debug("Client Thread to status(START)")
		else :
			if rsp=="WAITT":
				self.status="WAITT"
				logger.debug("Client Thread to status(WAITT)")
			else:
				logger.debug("Client Thread to  status(ERROR)")
				self.status="ERROR"
		return

	def START(self):
		ct=time.time()
		self.sg.sendStartSignal()# start mbuild
		self.Mo.start() 
		self.status="IDLLE"
		logger.debug("Client Thread to status(IDLLE)")
	def IDLLE(self):
		if self.retry>=1000:
			self.status="ERROR"
			logger.debug("Client Thread TIMEOUT(STATUS : IDLLE)")
			return
		try:
			msg=self.conn.recv(buffSize)
			self.retry=self.retry+1;
		except Exception as e:
			self.status="ERROR"
			logger.debug("Client Thread ERROR(STATUS : IDLLE)")	
			print e
		return	

	def WAITT(self):
		
		try:
			rsp=self.conn.recv(buffSize)
		except socket.timeout:
			self.status="ERROR"
			logger.debug("Client Thread ERROR(STATUS : WAITT)")	
			return
		if rsp=="START":
			self.status="START"
			logger.debug("Client Thread to status(START)")
			return

	def CLEAN(self):

		self.conn.close()
		self.sg.sendKillSignal()

class licenseClient(threading.Thread):
	def __init__(self) :
		host = 'Server IP'
		port = 4867 
		self.addr = (host,port)
		self.client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		self.client.settimeout(5)
		threading.Thread.__init__(self)

	def run(self)	:
		self.client.connect(self.addr)
		th=clientThread(self.client)
		logger.debug("clientThread(soc num : %s) created.",self.addr)
		th.start()
		
class MyMonitor(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
	def run(self):
		logger.debug("Monitoring mbuild start")

		while True:
			pid=subprocess.check_output("ps -e | grep mbuild | awk '{print $1}'|head -n 1",shell=True)
			if pid=="":
				logger.debug("mbuild process dead or finished. Shutting down client")
				os._exit(2)
			time.sleep(1)

def main():

	Client=licenseClient()
	Client.start()
if __name__ == "__main__":
	main()
