import sys
import socket
import threading as t
import re


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
                print('Error')
            else:
                msg = data.decode('utf-8')
                if "NEIGHBOUR" in msg:
                    cont = re.search(r'\w+:([0-9.]+)', msg)
                    viz = cont.group(1)
                    vizinhos.append(viz)
                    print(viz)
else:
    SERVER_PORT = int(sys.argv[1])


def client_worker(addr,port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((addr, port))
        s.sendall(bytes(input(),'utf-8'))
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
                data = conn.recv(1024)
                print(data)
                if not data:
                    break
                conn.sendall(data)

def main():
    while True:
        t1 = t.Thread(target=client_worker,args=(BOOTSTRAPPER_ADDRESS,SERVER_PORT))
        t2 = t.Thread(target=server_worker)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

main()