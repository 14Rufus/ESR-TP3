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
            if req == 'PING':
                closest_ip = self.rt.getShortestRoute()
                route = self.rt.getPercurso(closest_ip)
                ips = route.split(',')
                next_ip = ips[0]
                print(f'PINGING {next_ip}')
                p = Packet(self.ip,4)
                self.vizinhos[next_ip].send(p.encode())

    def updateVizinhos(self,ip,socket):
        self.vizinhos[ip] = socket