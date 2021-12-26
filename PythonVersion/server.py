import time, socket, sys, threading, os, util, atexit
from packet import Packet
from udp_packet import PacketUDP

class Server:

    def __init__(self):
        self.vizinhos = {}
        self.connected = []
        self.files_avaiable = [f for f in os.listdir('.') if os.path.isfile(f)]
        self.host = socket.gethostbyname(socket.gethostname())
        self.TCP_PORT = 9999
        self.UDP_PORT = 8888
        self.udp_socket = None
        self.streaming = False

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
                            print(f'{util.bcolors.OKBLUE}INFO: RECEIVED ALIVE SIGNAL FROM {origin_ip}{util.bcolors.ENDC}')
                            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                            self.vizinhos[origin_ip] = s
                            time.sleep(1)
                            s.connect((origin_ip,self.TCP_PORT))
                            self.connected.append(origin_ip)
                        else:
                            print(f'{util.bcolors.OKBLUE}INFO: {origin_ip} ALREADY CONNECTED TO SERVER{util.bcolors.ENDC}')
                    
                    elif packet_type == 'ASK_ROUTING':
                        print(f'{util.bcolors.OKBLUE}INFO: {origin_ip} ASKED FOR ROUTING TABLES{util.bcolors.ENDC}')
                        self.routing_signaler()
                    
                    elif packet_type == 'PING':
                        print(f'{util.bcolors.OKBLUE}INFO: GOT PING FROM {origin_ip}{util.bcolors.ENDC}')
                    
                    elif packet_type == 'IS_ALIVE':
                        ip_original = header_fields[2]
                        percurso = header_fields[4]
                        p = Packet(self.host, 8)
                        print(f'{util.bcolors.OKBLUE}INFO: ALIVE SIGNAL REQUESTED BY {origin_ip}{util.bcolors.ENDC}')
                        self.vizinhos[origin_ip].sendall(p.encodeAliveMessage(self.host, ip_original,percurso))
                        print(f'{util.bcolors.OKBLUE}INFO: SENT ALIVE CONFIRMATION{util.bcolors.ENDC}')
                    
                    elif packet_type == 'GET':
                        content = header_fields[2]
                        ip_destino = header_fields[3]
                        print(f'{util.bcolors.OKBLUE}INFO: GET REQUEST FROM {origin_ip} RECEIVED{util.bcolors.ENDC}')
                        udp_thread = threading.Thread(target=self.open_send_udp_socket,args=(content,origin_ip,ip_destino),daemon=True)
                        self.streaming = True
                        time.sleep(1)
                        udp_thread.start()

                    elif packet_type == 'SHUTDOWN':
                        print(f'{util.bcolors.OKBLUE}INFO : NEIGHBOUR {origin_ip} DISCONNECTED{util.bcolors.ENDC}')
                        self.connected.remove(origin_ip)
                        if self.streaming:
                            self.udp_socket.close()
                            self.streaming = False

                    elif packet_type == 'DEACTIVATE':
                        if self.streaming:
                            print(f'{util.bcolors.OKBLUE}INFO: CLIENT STOPPED STREAMING')
                            self.udp_socket.close()
                            self.streaming = False

            except Exception as e:
                print(e)
                print(F'{util.bcolors.FAIL}ERROR: Unknow Packet Type{util.bcolors.ENDC}')

    def create_sockets(self,vizinhos):
        aux = {}
        for viz in vizinhos:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # gethostbyname -> Devolve IP a partir do nome
                ip = socket.gethostbyname(viz)
                s.connect((ip,self.TCP_PORT))
                p = Packet(self.host,1)
                s.sendall(p.encodeRequest())
                print(f'{util.bcolors.OKBLUE}INFO: SENDING ALIVE SIGNAL TO {viz}@{ip}{util.bcolors.ENDC}')
                self.connected.append(ip)
                aux[ip] = s
            except Exception:
                aux[ip] = None
                print(f'{util.bcolors.WARNING}WARNING: {viz} NOT YET CONNECTED{util.bcolors.ENDC}')
        return aux

    def open_listen_tcp_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #stream = tcp    dgram = udp  inet = ipv4
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.TCP_PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                print(f'{util.bcolors.OKBLUE}INFO: RECEIVED NEW CLIENT CONNECTION{util.bcolors.ENDC}')
                threading.Thread(target=self.new_connection,args=(conn,addr),daemon=True).start()
    
    def open_send_udp_socket(self,req,address,ip_destino):
        time.sleep(2)
        file_size = os.path.getsize(req)
        num_of_packets = max(util.round_half_up(file_size/4096),1)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            self.udp_socket = s
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                print(f'{util.bcolors.OKBLUE}INFO: GET REQUEST FROM {address} TO SEND TO  {ip_destino}{util.bcolors.ENDC}')
                counter = 0
                if address in self.connected:
                    try:
                        with open(req) as f:
                            line_c = 0
                            content = ''
                            while line := f.readline():
                                content += line + '\n'
                                line_c += 1
                                if line_c ==  14:
                                    counter +=  1
                                    p = PacketUDP(self.host,1)
                                    print(f'{util.bcolors.OKBLUE}INFO: SENT PACKET #{counter}{util.bcolors.ENDC}')
                                    s.sendto(p.encodeData(ip_destino,counter,num_of_packets,content), (address,self.UDP_PORT))
                                    time.sleep(0.4)
                                    line_c = 0
                                    content = ''
                            # SEND SHUTDOWN UDP CONNECTION PACKET
                            p = PacketUDP(self.host, 2)
                            print(f'{util.bcolors.OKBLUE}INFO: SENDING SHUTDOWN UDP PACKET{util.bcolors.ENDC}')
                            s.sendto(p.encodeLast(),(address,self.UDP_PORT))
                            time.sleep(1)
                            return
                    except Exception as e:
                        print(f'{util.bcolors.FAIL}ERROR: STREAMING ERROR{util.bcolors.ENDC}')
                else:
                    return
            except Exception as e:
                print(e)
                print(F'{util.bcolors.FAIL}WARNING: UDP TRANSFER WENT WRONG{util.bcolors.ENDC}')
        
    def routing_signaler(self):
        time.sleep(2)
        for ip,s in self.vizinhos.items():
            if len(self.connected) != 0:
                try:
                    p = Packet(self.host, 2)
                    # server_ip metrica  estado  percurso files
                    fs_avaiable = ','.join(self.files_avaiable)
                    s.sendall(p.encodeRouting(self.host,0,0,'',fs_avaiable))
                    print(f'{util.bcolors.OKBLUE}INFO: SENT ROUTING SIGNAL TO {ip} FROM {self.host}{util.bcolors.ENDC}')
                except Exception as e:
                    self.connected.remove(ip)
                    print(e)
                    print(f'{util.bcolors.FAIL}ERROR: No Routing Signal sent{util.bcolors.ENDC}')

    def start(self,vizinhos):
        atexit.register(self.sendShutdownToNeighbours)
        t = threading.Thread(target=self.open_listen_tcp_socket,daemon=True)
        t.start()
        self.vizinhos = self.create_sockets(vizinhos)
        self.routing_signaler()
        try:
            t.join()
        except KeyboardInterrupt:
            print(f'{util.bcolors.OKBLUE}INFO: SHUTTING SERVER DOWN{util.bcolors.ENDC}')
    
    def sendShutdownToNeighbours(self):
        for ip,s in self.vizinhos.items():
                if len(self.connected) != 0:
                    if ip in self.connected:
                        p = Packet(self.host, 9)
                        s.sendall(p.encodeRequest())
                        print(f'{util.bcolors.OKBLUE}INFO: SENT SHUTDOWN SIGNAL TO {ip}{util.bcolors.ENDC}')
                        self.connected.remove(ip)