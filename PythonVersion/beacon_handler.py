import socket
import time
import sys

class Beacon():

    def __init__(self):
        self.sleep_time = 5
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def signal(self,addr,port):
        self.s.connect((addr,port))
        while True:
            try:
                time.sleep(self.sleep_time)
                print('SENDING SIGNAL BEACON TO SERVER')
                self.s.send(bytes('BEACON','utf-8'))
            except KeyboardInterrupt:
                sys.exit()