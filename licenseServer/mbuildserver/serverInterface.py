import threading
import socket
import sys
import logging
import os
import subprocess
import sys
import time
import signal
from time import ctime
from logging.handlers import RotatingFileHandler
server_queue=[]
bufSize=1024

################################################# log handler############################################
def LogHandler():
    logger=logging.getLogger('licenseServer')
    fileHandler=RotatingFileHandler('/home/sssw/licenseServer/log/licenseServer.log',maxBytes=1024*1024*100,backupCount=1)
    streamHandler=logging.StreamHandler()
   
    formatter=logging.Formatter('[%(levelname)s|%(filename)s.%(lineno)d] %(asctime)s >>> %(message)s]')
   
    fileHandler.setFormatter(formatter);
    streamHandler.setFormatter(formatter);
    
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.DEBUG);
   
    return logger

logger=LogHandler()

class serverThread(threading.Thread):
    def __init__(self,(conn,addr)):
        self.conn=conn
        self.addr=addr
        threading.Thread.__init__(self)
        self.status="INITT"
        self.retry=0
        self.conn.settimeout(10)
    
    def run(self):
        
        while True:
            func=getattr(self,self.status[:5].strip())
            func()
            if self.status=="ERROR":
                break;
            time.sleep(1)
        
	self.CLEAN()
        return

    def INITT(self):
        ret=self.CHECK()
        logger.debug("server thread(ip/conn : %s) running status(INIT) ",self.addr)
        if ret==True:
            self.status="START"
            logger.debug("server thread(ip/conn : %s) running status(START) ",self.addr)
        else :
            self.status="WAITT"
            logger.debug("server thread(ip/conn : %s) running status(WAITT) ",self.addr)

    def WAITT(self):   
        self.retry=self.retry+1
        if self.retry>=2000:
            self.status="ERROR"
            logger.debug("server thread(ip/conn : %s) WAIIT RETRY TIMEOUT",self.addr)
            return
        
        if self.CHECK()==True:
            logger.debug("server thread(ip/conn : %s) QUEUE FRONT ",self.addr)
            try :
                self.conn.send("START")
            except Exception as e:
                self.status="ERROR"
                logger.debug("server thread(ip/conn : %s) WAIIT RETRY TIMEOUT",self.addr)
            else :
                self.status="START"
                logger.debug("server thread(ip/conn : %s) running status(START)",self.addr)
                self.retry=0
        else :
            try:
                self.conn.send("WAITT")
                
            except Exception as e:
                self.status="ERROR"
                logger.debug("server thread(ip/conn : %s) WAIIT ERROR TIMEOUT",self.addr)
      
    def IDLLE(self):
        self.retry=self.retry+1
        if self.retry>=2000:
            self.status="ERROR"
            logger.debug("server thread(ip/conn : %s) IDLLE RETRY TIMEOUT",self.addr)
            return

        try:
            self.conn.send("IDLLE")
        except Exception as e:
            self.status="ERROR"
            logger.debug("server thread(ip/conn : %s) client disconnect detected(IDDLE) ",self.addr)
        
        return

    def START(self):
        try:
            self.conn.send("START")
        except Exception as e:
            self.status="ERROR"
            logger.debug("server thread(ip/conn : %s) START ERROR",self.addr)
        else :
            logger.debug("server thread(ip/conn : %s) running status(IDLLE)",self.addr)
            self.status="IDLLE"
        
    def CHECK(self):
        return check_server_queue((self.conn,self.addr))
        
    def CLEAN(self):
        remove_from_queue(self.conn,self.addr)
   	logger.debug("server thread(ip/conn : %s) removed from queue(current queue size = %d)",self.addr,len(serverThread_queue))
        logger.debug("server thread(ip/conn : %s) closing socket",self.addr)
        self.conn.close()
    
class LicenseServer(threading.Thread):
    def __init__(self):
        addr=('',4867)
        self.server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) # TCP socket
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(addr)      
        threading.Thread.__init__(self)
        self.server_socket.listen(5)
    def __del__(self):
        self.server_socket.close()

    def run(self):
        while True:
            client ,client_addr=self.server_socket.accept()        
            th=serverThread((client,client_addr))
            serverThread_queue.append((client,client_addr))
            logger.info("server Thread created(soc num:%s) server queue size %d",client_addr,len(serverThread_queue))
            th.start()

####################################### UTILS #######################################

def check_server_queue((conn,addr)):
    if serverThread_queue[0]==(conn,addr): # my turn
        return True
    return False

def remove_from_queue(conn,addr):
    try:
        serverThread_queue.remove((conn,addr))
    except Exception as e:
        print e
