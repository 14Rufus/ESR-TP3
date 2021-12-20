class Packet:

    def __init__(self,ip,tipo):
        self.origin_ip = ip
        self.packet_type = self.getType(tipo)

    def getOriginIP(self):
        return self.origin_ip

    def getType(self,tipo):
        tipos = {
            1 : 'ALIVE',
            2 : 'GET'
        }
        return tipos[tipo]

    def encode(self):
        msg = self.origin_ip + ';' + self.packet_type
        return bytes(msg,'utf-8')
