import time, socket, sys, threading
from packet import Packet
from routes import RouteTable

class Node:

    def __init__(self):
        self.vizinhos = {}
        self.connected = []
        self.host = socket.gethostbyname(socket.gethostname())
        self.TCP_PORT = 9999
        self.UDP_PORT = 8888 
        self.rt = RouteTable()

    def start(self,vizinhos):
        t = threading.Thread(target=self.open_listen_tcp_socket,daemon=True)
        t.start()
        self.vizinhos = self.create_sockets(vizinhos)
        t.join()


    def open_listen_tcp_socket(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host,self.TCP_PORT))
                s.listen()
                while True:
                    #print('Listening for new connections')
                    conn, addr = s.accept()
                    t = threading.Thread(target=self.open_send_tcp_socket,args=(conn,addr),daemon=True)
                    t.start()
        except Exception:
            for ip,s in self.vizinhos.items():
                if s == client_socket:
                    self.connected.pop(ip)
                    del self.vizinhos[ip]
            conn.close()

    def open_send_tcp_socket(self,conn,addr):
        try:
            while data := conn.recv(1024):
                    if not data:
                        break
                    else:
                        content = data.decode('utf-8')
                        header_fields = content.split(';')
                        origin_ip = header_fields[0]
                        packet_type = header_fields[1]
                        if packet_type == 'ALIVE':
                            if origin_ip in self.connected:
                                print('NODE ALREADY REGISTERED\n')
                            else:
                                print(f'RECEIVED ALIVE SIGNAL FROM {origin_ip}')
                                p = Packet(self.host,1)
                                conn.sendall(p.encode())
                                self.connected.append(origin_ip)
                        elif packet_type == 'ROUTING':
                            metric = int(header_fields[2])
                            print(f'RECEIVED ROUTING SIGNAL FROM {origin_ip}')
                            self.rt.add_route(origin_ip,metric)
                            self.rout_neighbours(origin_ip,metric+1)
                        else:
                            print('Unknow Packet Type')
        except Exception:
            for ip,s in self.vizinhos.items():
                if s == client_socket:
                    self.connected.pop(ip)
                    del self.vizinhos[ip]
            conn.close()

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
                print(f'ERROR: {viz} NOT YET CONNECTED')
            aux[ip] = s
        return aux

    def rout_neighbours(self,oip,metric):
        for ip in self.vizinhos.keys():
            if len(self.connected) != 0:
                if ip == oip or ip not in self.connected:
                    continue
                else:
                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                    try:
                        s.connect((ip,self.TCP_PORT))
                        p = Packet(self.host, 2)
                        s.sendall(p.encodeRouting(metric))
                        print(f'SENT ROUTING SIGNAL TO {ip} FROM {self.host}')
                    except Exception as e:
                        print(e)
                        print('No Routing Signal sent')