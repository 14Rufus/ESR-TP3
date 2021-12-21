import time, socket, sys, threading
from packet import Packet

class Server:

    def __init__(self):
        self.vizinhos = {}
        self.connected = []
        self.host = socket.gethostbyname(socket.gethostname())
        self.TCP_PORT = 9999
        self.UDP_PORT = 8888

    def new_connection(self,client_socket,addr):
        while data := client_socket.recv(1024):
            try:
                content = data.decode('utf-8')
                header_fields = content.split(';')
                origin_ip = header_fields[0]
                packet_type = header_fields[1]
                if not data:
                    break
                else:
                    if packet_type == 'ALIVE':
                        if origin_ip not in self.connected:
                            p = Packet(self.host, 1)
                            client_socket.sendall(p.encode())
                            self.connected.append(origin_ip)
                            time.sleep(1)
                            self.routing_signaler()
                        else:
                            print(f'{origin_ip} Already Connected to Server')
            except Exception:
                for ip,s in self.vizinhos.items():
                    if s == client_socket:
                        self.connected.pop(ip)
                        self.vizinhos.pop(ip)
                client_socket.close()

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
                print(f'{viz} NOT YET CONNECTED')
            aux[ip] = s
        return aux

    def open_listen_tcp_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #stream = tcp    dgram = udp  inet = ipv4
            s.bind((self.host, self.TCP_PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                if conn not in self.vizinhos.values():
                    print('RECEIVED NEW CLIENT CONNECTION')
                    threading.Thread(target=self.new_connection,args=(conn,addr),daemon=True).start()
    
    def routing_signaler(self):
        while True:
            time.sleep(20)
            for ip in self.vizinhos.keys():
                if len(self.connected) != 0:
                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                    try:
                        s.connect((ip,self.TCP_PORT))
                        p = Packet(self.host, 2)
                        s.sendall(p.encodeRouting(1))
                        print(f'SENT ROUTING SIGNAL TO {ip} FROM {self.host}')
                    except Exception as e:
                        print(e)
                        print('No Routing Signal sent')

    def start(self,vizinhos):
        t = threading.Thread(target=self.open_listen_tcp_socket,daemon=True)
        t.start()
        self.vizinhos = self.create_sockets(vizinhos)
        r = threading.Thread(target=self.routing_signaler,daemon=True)
        r.start()
        t.join()
        r.join()