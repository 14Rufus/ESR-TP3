import time, socket, sys, threading
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

    def start(self,vizinhos):
        t = threading.Thread(target=self.open_listen_tcp_socket,daemon=True)
        c = threading.Thread(target=self.ch.handleRequests,daemon=True)
        t.start()
        self.vizinhos = self.create_sockets(vizinhos)
        c.start()
        t.join()


    def open_listen_tcp_socket(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host,self.TCP_PORT))
            s.listen()
            while True:
                #print('Listening for new connections')
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
                    if packet_type == 'ALIVE':
                        if origin_ip in self.connected:
                            print('INFO: NODE ALREADY REGISTERED\n')
                        else:
                            print(f'INFO: RECEIVED ALIVE SIGNAL FROM {origin_ip}')
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.vizinhos[origin_ip] = s
                            self.ch.updateVizinhos(origin_ip,s)
                            time.sleep(1)
                            s.connect((origin_ip,self.TCP_PORT))
                            self.connected.append(origin_ip)
                    elif packet_type == 'ROUTING':
                        print(f'INFO: RECEIVED ROUTING SIGNAL FROM {origin_ip}')
                        if self.rt.existsRoute(origin_ip) != 'None':
                            print('ERROR : ROUTE ALREADY EXISTS')
                        else:
                            jumps = int(header_fields[2]) + 1 
                            state = int(header_fields[3])
                            route = header_fields[4]
                            if route == '':
                                new_route = origin_ip
                            else:
                                new_route = origin_ip + ',' + route
                            print('INFO: ADDED NEW ROUTE')
                            self.rt.add_route(origin_ip,jumps,state,new_route)
                            self.rout_neighbours(origin_ip,jumps,state,new_route)
                    elif packet_type == 'ASK_ROUTING':
                            print(f'INFO: {origin_ip} ASKED FOR ROUTING TABLES')
                            if (route := self.rt.getShortestRoute()) != None:
                                p = Packet(self.host, 2)
                                jumps = self.rt.getJumps(route)
                                state = self.rt.getState(route)
                                percurso = self.rt.getPercurso(route)
                                self.vizinhos[origin_ip].sendall(p.encodeRouting(jumps,state,percurso))
                                print('INFO: ROUTING INFORMATION SENT')
                            else:
                                print('WARNING: NO ROUTING TABLE INFORMATION FOUND')
                    elif packet_type == 'PING':
                        closest_ip = self.rt.getShortestRoute()
                        route = self.rt.getPercurso(closest_ip)
                        ips = route.split(',')
                        next_ip = ips[0]
                        print(f'INFO: PING FROM {origin_ip} NOW GOING TO {next_ip}')
                        p = Packet(self.host,4)
                        self.vizinhos[next_ip].send(p.encode())
                    else:
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
                p2 = Packet(self.host, 3)
                time.sleep(1)
                s.sendall(p2.encode())
                print(f'INFO: ASKING {viz} FOR ROUTING TABLES')
                self.connected.append(ip)
                aux[ip] = s
                self.ch.updateVizinhos(ip,s)
            except Exception:
                print(f'WARNING: {viz} NOT YET CONNECTED')
                aux[ip] = None
        return aux

    def rout_neighbours(self,oip,jumps,state,route):
        for ip,s in self.vizinhos.items():
            if len(self.connected) != 0:
                if ip == oip or ip not in self.connected:
                    continue
                else:
                    #s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                    try:
                        #s.connect((ip,self.TCP_PORT))
                        p = Packet(self.host, 2)
                        s.sendall(p.encodeRouting(jumps,state,route))
                        print(f'INFO: SENT ROUTING SIGNAL TO {ip} FROM {self.host}')
                    except Exception as e:
                        self.connected.remove(ip)
                        print(e)
                        print('ERROR: No Routing Signal sent')