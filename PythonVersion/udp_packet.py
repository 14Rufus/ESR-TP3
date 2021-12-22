class PacketUDP:

    def __init__(self,ip):
        self.ip_origem = ip

    def encode(self,ip_destino,counter,num_of_packets,content):
        msg = self.ip_origem + ';' + ip_destino + ';' + str(counter) + ';' + str(num_of_packets) + ';' + content
        return bytes(msg,'utf-8')
