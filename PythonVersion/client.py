import socket
import sys

HOST = sys.argv[1]  # The server's hostname or IP address
PORT = int(sys.argv[2])        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes(f"Connecting from {HOST}",'utf-8'))
    while True:
        #s.send(bytes(input(),'utf-8'))
        data = s.recv(1024)
        msg = data.decode('utf-8')
        print(msg)