class PacketUDP:

    def __init__(self,ip,tipo):
        self.ip_origem = ip
        self.packet_type = self.getTipo(tipo)

    def encodeData(self,ip_destino,counter,num_of_packets,content):
        msg = self.ip_origem + ';' + self.packet_type + ';' + ip_destino + ';' + str(counter) + ';' + str(num_of_packets) + ';' + content
        return bytes(msg,'utf-8')

    def encodeLast(self):
        msg = self.ip_origem + ';' + self.packet_type
        return bytes(msg, 'utf-8')

    def getTipo(self,tipo):
        tipos = {
            1 : 'DATA',
            2 : 'LAST'
        }
        return tipos[tipo]