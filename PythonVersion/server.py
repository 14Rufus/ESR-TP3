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
                            print(f'INFO: RECEIVED ALIVE SIGNAL FROM {origin_ip}')
                            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                            self.vizinhos[origin_ip] = s
                            time.sleep(1)
                            s.connect((origin_ip,self.TCP_PORT))
                            self.connected.append(origin_ip)
                        else:
                            print(f'INFO: {origin_ip} ALREADY CONNECTED TO SERVER')
                    elif packet_type == 'ASK_ROUTING':
                        print(f'INFO: {origin_ip} ASKED FOR ROUTING TABLES')
                        self.routing_signaler()
                    elif packet_type == 'PING':
                        print(f'INFO: GOT PING FROM {origin_ip}')
            except Exception as e:
                print(e)
                print('ERROR: Unknow Packet Type')

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
                print(f'INFO: SENDING ALIVE SIGNAL TO {viz}@{ip}')
                self.connected.append(ip)
                aux[ip] = s
            except Exception:
                aux[ip] = None
                print(f'WARNING: {viz} NOT YET CONNECTED')
        return aux

    def open_listen_tcp_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #stream = tcp    dgram = udp  inet = ipv4
            s.bind((self.host, self.TCP_PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                print('INFO: RECEIVED NEW CLIENT CONNECTION')
                threading.Thread(target=self.new_connection,args=(conn,addr),daemon=True).start()
    
    def routing_signaler(self):
        #while True:
            time.sleep(2)
            for ip,s in self.vizinhos.items():
                if len(self.connected) != 0:
                    #s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                    try:
                        p = Packet(self.host, 2)
                        # metrica  estado  percurso
                        s.sendall(p.encodeRouting(0,0,''))
                        print(f'INFO: SENT ROUTING SIGNAL TO {ip} FROM {self.host}')
                    except Exception as e:
                        self.connected.remove(ip)
                        print(e)
                        print('ERROR: No Routing Signal sent')

    def start(self,vizinhos):
        t = threading.Thread(target=self.open_listen_tcp_socket,daemon=True)
        t.start()
        self.vizinhos = self.create_sockets(vizinhos)
        self.routing_signaler()
        t.join()