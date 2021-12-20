import socket
import sys
import threading

class Server:

    def __init__(self):
        self.vizinhos = {}
        self.host = socket.gethostbyname(socket.gethostname())
        self.TCP_PORT = 9999
        self.UDP_PORT = 8888

    def new_connection(self,client_socket,addr):
        while True:
            try:
                data = client_socket.recv(1024)
                print('Connected by', addr)
                if not data:
                    break
                else:
                    print(data)
                    #client_socket.sendall(bytes(f"Connected to server at {addr}",'utf-8'))
            except KeyboardInterrupt:
                client_socket.close()

    def create_sockets(self,vizinhos):
        aux = {}
        for viz in vizinhos:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # gethostbyname -> Devolve IP a partir do nome
                ip = socket.gethostbyname(viz)
                s.connect((ip,self.TCP_PORT))
                s.sendall(bytes('ALIVE','utf-8'))
                print(f'SENT ALIVE SIGNAL TO {ip}')
            except Exception:
                print(f'{viz} NO YET CONNECTED')
            aux[ip] = s
        return aux

    def open_listen_tcp_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #stream = tcp    dgram = udp  inet = ipv4
            s.bind((self.host, self.TCP_PORT))
            s.listen()
            while True:
                print('AWAITING NEW CLIENT CONNECTION')
                conn, addr = s.accept()
                threading.Thread(target=self.new_connection,args=(conn,addr),daemon=True).start()
    
    def start(self,vizinhos):
        t = threading.Thread(target=self.open_listen_tcp_socket,daemon=True)
        self.vizinhos = self.create_sockets(vizinhos)
        t.start()
        t.join()