import socket
import sys
import threading
import time
from packet import Packet

class Node:

    def __init__(self):
        self.vizinhos = {}
        self.connected = []
        self.host = socket.gethostbyname(socket.gethostname())
        self.TCP_PORT = 9999
        self.UDP_PORT = 8888

    def start(self,vizinhos):
        t = threading.Thread(target=self.open_listen_tcp_socket,daemon=True)
        t.start()
        self.vizinhos = self.create_sockets(vizinhos)
        t.join()


    def open_listen_tcp_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host,self.TCP_PORT))
            s.listen()
            while True:
                print('Listening for new connections')
                conn, addr = s.accept()
                t = threading.Thread(target=self.open_send_tcp_socket,args=(conn,addr),daemon=True)
                t.start()

    def open_send_tcp_socket(self,conn,addr):
        while data := conn.recv(1024):
            if not data:
                break
            else:
                content = data.decode('utf-8')
                header_fields = content.split(';')
                origin_ip = header_fields[0]
                packet_type = header_fields[1]
                if packet_type == 'ALIVE' and origin_ip in self.connected:
                    print('NODE ALREADY REGISTERED\n')
                else:
                    print(f'RECEIVED ALIVE SIGNAL FROM {origin_ip}')
                    conn.sendall(b'ALIVE')
                    self.connected.append(origin_ip)

    def create_sockets(self,vizinhos):
        aux = {}
        for viz in vizinhos:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # gethostbyname -> Devolve IP a partir do nome
                ip = socket.gethostbyname(viz)
                s.connect((ip,self.TCP_PORT))
                p = Packet(self.host,1)
                s.sendall(p.encode())
                print(f'SENDING ALIVE SIGNAL TO {viz}@{ip}')
                self.connected.append(ip)
            except Exception:
                print(f'ERROR: {viz} NO YET CONNECTED')
            aux[ip] = s
        return aux
