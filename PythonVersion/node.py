import time, socket, sys, threading, util, atexit
from packet import Packet
from routes import RouteTable
from clienthandler import ClientHandler

class Node:

    def __init__(self):
        self.vizinhos = {}
        self.connected = []
        self.host = socket.gethostbyname(socket.gethostname())
        self.TCP_PORT = 9999
        self.UDP_PORT = 8888 
        self.rt = RouteTable()
        self.ch = ClientHandler(self.host,self.vizinhos, self.rt)
        self.streaming = False
        self.udp_socket = None

    def start(self,vizinhos):
        atexit.register(self.sendShutdownToNeighbours)
        t = threading.Thread(target=self.open_listen_tcp_socket,daemon=True)
        c = threading.Thread(target=self.ch.handleRequests,daemon=True)
        t.start()
        self.vizinhos = self.create_sockets(vizinhos)
        c.start()
        try:
            t.join()
        except KeyboardInterrupt:
            print(f'{util.bcolors.WARNING}SHUTTING DOWN{util.bcolors.ENDC}')


    def open_listen_tcp_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host,self.TCP_PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=self.open_send_tcp_socket,args=(conn,addr),daemon=True)
                t.start()

    def open_listen_udp_socket(self,ip):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            self.udp_socket = s
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((self.host,self.UDP_PORT))
                while True:
                    data, addr = s.recvfrom(20480)
                    if not data:
                        break
                    else:
                        if ip in self.connected:
                            content = data.decode('utf-8')
                            header = content.split(';')
                            packet_type = header[1]
                            if packet_type == 'DATA':
                                self.streaming = True
                                print(f'{util.bcolors.OKBLUE}INFO: RECEIVED PACKET #{header[3]}{util.bcolors.ENDC}')
                                s.sendto(data, (ip,self.UDP_PORT))
                                print(f'{util.bcolors.OKBLUE}INFO: SENDING TO {ip}{util.bcolors.ENDC}')
                            elif packet_type == 'LAST':
                                self.streaming = False
                                print(f'{util.bcolors.OKBLUE}INFO: SHUTTING DOWN UDP CONNECTION{util.bcolors.ENDC}')
                                s.sendto(data, (ip,self.UDP_PORT))
                                self.rt.setRouteInactive(header[0])
                                time.sleep(1)
                                return
                        else:
                            return
            except Exception as e:
                print(e)
                print(f'{util.bcolors.FAIL}ERROR: STREAMING ERROR{util.bcolors.ENDC}')

    def open_send_tcp_socket(self,conn,addr):
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
                            print(f'{util.bcolors.OKBLUE}INFO: NODE ALREADY REGISTERED{util.bcolors.ENDC}')
                        else:
                            print(f'{util.bcolors.OKBLUE}INFO: RECEIVED ALIVE SIGNAL FROM {origin_ip}{util.bcolors.ENDC}')
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.vizinhos[origin_ip] = s
                            self.ch.updateVizinhos(origin_ip,s)
                            time.sleep(1)
                            s.connect((origin_ip,self.TCP_PORT))
                            self.connected.append(origin_ip)
                    
                    elif packet_type == 'ROUTING':
                        print(f'{util.bcolors.OKBLUE}INFO: RECEIVED ROUTING SIGNAL FROM {origin_ip}{util.bcolors.ENDC}')
                        if self.rt.existsRoute(origin_ip) != 'None':
                            print(f'{util.bcolors.FAIL}ERROR : ROUTE ALREADY EXISTS{util.bcolors.ENDC}')
                        else:
                            server_ip = header_fields[2]
                            jumps = int(header_fields[3]) + 1 
                            state = int(header_fields[4])
                            route = header_fields[5]
                            files_avaiable = header_fields[6]
                            if route == '':
                                new_route = origin_ip
                            else:
                                new_route = origin_ip + ',' + route
                            print(f'{util.bcolors.OKBLUE}INFO: ADDED NEW ROUTE{util.bcolors.ENDC}')
                            self.rt.add_route(origin_ip,jumps,state,new_route,server_ip,files_avaiable)
                            self.rout_neighbours(origin_ip,jumps,state,new_route,server_ip,files_avaiable)
                    
                    elif packet_type == 'ASK_ROUTING':
                            print(f'{util.bcolors.OKBLUE}INFO: {origin_ip} ASKED FOR ROUTING TABLES{util.bcolors.ENDC}')
                            if (route := self.rt.getShortestRoute()) != None:
                                p = Packet(self.host, 2)
                                server_ip = self.rt.getServerAddress(route)
                                jumps = self.rt.getJumps(route)
                                state = self.rt.getState(route)
                                percurso = ','.join(self.rt.getPercurso(route))
                                files = ','.join(self.rt.getFilesAvaiable(route))
                                self.vizinhos[origin_ip].sendall(p.encodeRouting(server_ip,jumps,state,percurso,files))
                                print(f'{util.bcolors.OKBLUE}INFO: ROUTING INFORMATION SENT{util.bcolors.ENDC}')
                            else:
                                print(f'{util.bcolors.WARNING}WARNING: NO ROUTING TABLE INFORMATION FOUND{util.bcolors.ENDC}')
                    
                    elif packet_type == 'PING':
                        closest_ip = self.rt.getShortestRoute()
                        route = self.rt.getPercurso(closest_ip)
                        next_ip = route[0]
                        print(f'{util.bcolors.OKBLUE}INFO: PING FROM {origin_ip} NOW GOING TO {next_ip}{util.bcolors.ENDC}')
                        p = Packet(self.host,4)
                        self.vizinhos[next_ip].sendall(p.encodeRequest())
                    
                    elif packet_type == 'IS_ALIVE':
                        ip_origem = header_fields[2]
                        ip_destino = header_fields[3]
                        percurso_antigo = header_fields[4]
                        percurso_novo = self.host + ',' + percurso_antigo
                        closest_ip = self.rt.getShortestRoute()
                        route = self.rt.getPercurso(closest_ip)
                        next_ip = route[0]
                        p = Packet(self.host, 7)
                        self.vizinhos[next_ip].sendall(p.encodeAliveMessage(ip_origem, ip_destino,percurso_novo))
                    
                    elif packet_type == 'SHUTDOWN':
                        print(f'{util.bcolors.OKBLUE}INFO : NEIGHBOUR {origin_ip} DISCONNECTED{util.bcolors.ENDC}')
                        if self.streaming:
                            self.udp_socket.close()
                            self.streaming = False
                        self.rt.updateOnNeighbourShutdown(origin_ip)
                        self.ch.updateVizinhos(origin_ip, None)
                        print(f'{util.bcolors.OKBLUE}WARNING NEIGHBOURS TO DELETE ROUTE{util.bcolors.ENDC}')
                        self.warnNeighboursRouteInactive()
                        self.connected.remove(origin_ip)

                    elif packet_type == 'AM_ALIVE':
                        ip_origem = header_fields[2]
                        ip_destino = header_fields[3]
                        percurso_antigo = header_fields[4]
                        ips = percurso_antigo.split(',')
                        percurso_novo = ','.join(ips[1:])
                        if ip_destino == self.host:
                            print(f'{util.bcolors.OKBLUE}INFO: GOT ALIVE CONFIRMATION FROM {origin_ip}{util.bcolors.ENDC}')
                            self.rt.setRouteActive(origin_ip)
                            print(f'{util.bcolors.OKBLUE}INFO: FOUND ACTIVE ROUTE{util.bcolors.ENDC}')

                        else:
                            print(f'{util.bcolors.OKBLUE}INFO: GOT ALIVE CONFIRMATION FROM {origin_ip}{util.bcolors.ENDC}')
                            self.rt.setRouteActive(origin_ip)
                            p = Packet(self.host,8)
                            print(f'{util.bcolors.OKBLUE}INFO : SENDING ALIVE CONFIRMATION TO {ips[1]}{util.bcolors.ENDC}')
                            self.vizinhos[ips[1]].sendall(p.encodeAliveMessage(ip_origem, ip_destino, percurso_novo))
                    
                    elif packet_type == 'GET':
                        udp = threading.Thread(target=self.open_listen_udp_socket,args=(origin_ip,),daemon=True)
                        if not self.streaming:
                            self.streaming = True
                            content = header_fields[2]
                            closest_ip = self.rt.getShortestRoute()
                            route = self.rt.getPercurso(closest_ip)
                            next_ip = route[0]
                            ip_origem = header_fields[3]
                            print(f'{util.bcolors.OKBLUE}INFO: GET REQUEST FROM {origin_ip} NOW GOING TO {next_ip}{util.bcolors.ENDC}')
                            p = Packet(self.host, 6)
                            self.vizinhos[next_ip].sendall(p.encodeGetRequest(content,ip_origem))
                            time.sleep(1)
                        udp.start()
                        udp.join()
                    
                    elif packet_type == 'DEACTIVATE':
                        self.rt.setRouteInactive(origin_ip)

                    else:
                        print(f'{util.bcolors.FAIL}ERROR: Unknow Packet Type{util.bcolors.ENDC}')


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
                p2 = Packet(self.host, 3)
                time.sleep(1)
                s.sendall(p2.encodeRequest())
                print(f'{util.bcolors.OKBLUE}INFO: ASKING {viz} FOR ROUTING TABLES{util.bcolors.ENDC}')
                self.connected.append(ip)
                aux[ip] = s
                self.ch.updateVizinhos(ip,s)
            except Exception:
                print(f'{util.bcolors.WARNING}WARNING: {viz} NOT YET CONNECTED{util.bcolors.ENDC}')
                aux[ip] = None
        return aux

    def rout_neighbours(self,oip,jumps,state,route,server_ip,files_avaiable):
        for ip,s in self.vizinhos.items():
            if len(self.connected) != 0:
                if ip == oip or ip not in self.connected:
                    continue
                else:
                    try:
                        p = Packet(self.host, 2)
                        s.sendall(p.encodeRouting(server_ip,jumps,state,route,files_avaiable))
                        print(f'{util.bcolors.OKBLUE}INFO: SENT ROUTING SIGNAL TO {ip} FROM {self.host}{util.bcolors.ENDC}')
                    except Exception as e:
                        self.connected.remove(ip)
                        print(e)
                        print(f'{util.bcolors.FAIL}ERROR: No Routing Signal Sent{util.bcolors.ENDC}')
    
    def sendShutdownToNeighbours(self):
        for ip,s in self.vizinhos.items():
                if len(self.connected) != 0:
                    if ip in self.connected:
                        p = Packet(self.host, 9)
                        s.sendall(p.encodeRequest())
                        print(f'{util.bcolors.OKBLUE}INFO: SENT SHUTDOWN SIGNAL TO {ip}{util.bcolors.ENDC}')
                        self.connected.remove(ip)

    def warnNeighboursRouteInactive(self):
        for ip,s in self.vizinhos.items():
                if len(self.connected) != 0:
                    if ip in self.connected:
                        p = Packet(self.host, 10)
                        s.sendall(p.encodeRequest())
