import sys
import socket
import threading as t
import re
from beacon_handler import Beacon

HOST = socket.gethostbyname(socket.gethostname())

vizinhos = []
if sys.argv[1] == 'bootstrapper':
    SERVER_PORT = int(sys.argv[3])
    BOOTSTRAPPER_ADDRESS = sys.argv[2]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((BOOTSTRAPPER_ADDRESS, SERVER_PORT))
        s.sendall(b'REQUEST NEIGHBOURS')
        while True:
            data = s.recv(1024)
            if not data:
                print('EXITING NEIGHOUR GATHERING')
                break
            else:
                msg = data.decode('utf-8')
                if "NEIGHBOUR" in msg:
                    cont = re.search(r'\w+:([0-9.]+)', msg)
                    viz = cont.group(1)
                    vizinhos.append(viz)
                    print(viz)
else:
    SERVER_ADDRESS = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])


def client_worker(addr,port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, port))
        s.sendall(bytes('Hello','utf-8'))
        while True:
            data = s.recv(1024)
            msg = data.decode('utf-8')
            print(msg)

def server_worker():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, SERVER_PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                try:
                    data = conn.recv(1024)
                    print(data)
                    if not data:
                        break
                    conn.sendall(data)
                except KeyboardInterrupt:
                    sys.exit()

def main():
    b = Beacon()
    print('CREATING CLIENT THREAD FOR OTT')
    t1 = t.Thread(target=client_worker,args=(BOOTSTRAPPER_ADDRESS,SERVER_PORT),daemon=True)
    print('CREATING SERVER THREAD FOR OTT')
    t2 = t.Thread(target=server_worker,daemon=True)
    print('CREATING BEACON THREAD FOR OTT')
    t3 = t.Thread(target=b.signal,args=(SERVER_ADDRESS,SERVER_PORT),daemon=True)    
    t1.start()
    t2.start()
    t3.start()


main()