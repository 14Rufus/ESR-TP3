import socket, time , threading, util
from routes import RouteTable
from packet import Packet
from udp_packet import PacketUDP

class ClientHandler():

    def __init__(self,ip,vizinhos,rotas):
        self.ip = ip
        self.vizinhos = vizinhos
        self.rt = rotas
        self.UDP_PORT = 8888

    def handleRequests(self):
        while True:
            req = input(f'{util.bcolors.OKGREEN}SERVER>>{util.bcolors.ENDC}')
            if req != '':
                pass
                if (closest_ip := self.rt.getShortestRoute()) != None:
                    if req.upper() == 'PING':
                        route = self.rt.getPercurso(closest_ip)
                        next_ip = route[0]
                        print(f'PINGING {next_ip}')
                        p = Packet(self.ip,4)
                        self.vizinhos[next_ip].sendall(p.encodeRequest())
                    elif req.upper() == 'TABLE':
                        print(self.rt.getTable())
                    elif req.upper() == 'CLOSEST':
                        print(closest_ip)
                    elif req.upper() == 'SETUP':
                        route = self.rt.getPercurso(closest_ip)
                        next_ip = route[0]
                        print(f'{util.bcolors.OKBLUE}INFO: LOOKING FOR AVAIABLE ROUTE{util.bcolors.ENDC}')
                        p = Packet(self.ip, 7)
                        ip_destino = self.rt.getServerAddress(closest_ip)
                        try:
                            self.vizinhos[next_ip].sendall(p.encodeAliveMessage(self.ip,ip_destino,self.ip))
                        except Exception:
                            print(f'{util.bcolors.WARNING}WARNING: NEIGHBOUR NOT CONNECTED{util.bcolors.ENDC}')
                    elif 'GET' in req.upper():
                        route = self.rt.getPercurso(closest_ip)
                        next_ip = route[0]
                        content = req[4:]
                        if self.rt.getState(closest_ip) == 1:
                            if content in self.rt.getFilesAvaiable(closest_ip):
                                p = Packet(self.ip,6)
                                self.vizinhos[next_ip].sendall(p.encodeGetRequest(content,self.ip))
                                threading.Thread(target=self.udp_listener,daemon=True).start()
                            else:
                                print(f'{util.bcolors.WARNING}WARNING: FILE NOT AVAIABLE{util.bcolors.ENDC}')
                        else:
                            print(f'{util.bcolors.WARNING}WARNING: NO ROUTES AVAIABLE{util.bcolors.ENDC}')
                    else:
                        pass
                else:
                    print(f'{util.bcolors.WARNING}WARNING: NO ROUTE AVAIABLE{util.bcolors.ENDC}')

    def updateVizinhos(self,ip,socket):
        self.vizinhos[ip] = socket

    def udp_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.ip,self.UDP_PORT))
            while True:
                try:
                    #current_packet = 0 # Devia verificar se o frame que vai receber é o seguinte ao atual
                    data, addr = s.recvfrom(20480)
                    # ip_quem_enviou, ip_final, counter, total_pacotes, conteudo
                    pacote = data.decode('utf-8')
                    fields = pacote.split(';')
                    packet_type = fields[1]
                    if packet_type == 'DATA':
                        counter = int(fields[3])
                        num_of_packets = float(fields[4])
                        content = fields[5].encode('ascii','ignore')
                        print(content.decode('ascii','ignore'))
                    elif packet_type == 'LAST':
                        print(f'{util.bcolors.OKBLUE}INFO: SHUTTING DOWN UDP CONNECTION{util.bcolors.ENDC}')
                        return
                except Exception as e:
                    print(e)
                    print(f'{util.bcolors.FAIL}ERROR: SOMETHING WENT WRONG AT RECEIVING PACKET{util.bcolors.ENDC}')