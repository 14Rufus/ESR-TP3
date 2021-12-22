import socket
import time
from routes import RouteTable
from packet import Packet

class ClientHandler():

    def __init__(self,ip,vizinhos,rotas):
        self.ip = ip
        self.vizinhos = vizinhos
        self.rt = rotas
        self.TCP_PORT = 9999
        self.UDP_PORT = 8888

    def handleRequests(self):
        while True:
            req = input('SERVER>>')
            if (closest_ip := self.rt.getShortestRoute()) != None:
                if req.upper() == 'PING':
                    route = self.rt.getPercurso(closest_ip)
                    ips = route.split(',')
                    next_ip = ips[0]
                    print(f'PINGING {next_ip}')
                    p = Packet(self.ip,4)
                    self.vizinhos[next_ip].send(p.encode())
                elif req.upper() == 'TABLE':
                    print(self.rt.getTable())
                elif req.upper() == 'CLOSEST':
                    if (closest_ip := self.rt.getShortestRoute()) != None:
                        print(closest_ip)
                    else:
                        print('WARNING: NO ROUTE AVAIABLE')
                elif 'GET' in req.upper():
                    route = self.rt.getPercurso(closest_ip)
                    ips = route.split(',')
                    next_ip = ips[0]
                    content = req[4:]
                    p = Packet(self.ip,5)
                    self.vizinhos[next_ip].send(p.encodeGetRequest(content))
            else:
                print('WARNING: NO ROUTE AVAIABLE')

    def updateVizinhos(self,ip,socket):
        self.vizinhos[ip] = socket