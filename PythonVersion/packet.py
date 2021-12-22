class Packet:

    def __init__(self,ip,tipo):
        self.origin_ip = ip
        self.packet_type = self.getType(tipo)

    def getOriginIP(self):
        return self.origin_ip

    def getType(self,tipo):
        tipos = {
            1 : 'ALIVE',
            2 : 'ROUTING',
            3 : 'ASK_ROUTING',
            4 : 'PING',
            5 : 'SETUP',
            6 : 'GET',
            7 : 'IS_ALIVE',
            8 : 'AM_ALIVE',
            9 : 'SHUTDOWN'
        }
        return tipos[tipo]

    def encodeRequest(self):
        msg = self.origin_ip + ';' + self.packet_type
        return bytes(msg,'utf-8')

    def encodeRouting(self,server_ip,routing_value,state,percurso,ficheiros):
        msg = self.origin_ip + ';' + self.packet_type + ';' + server_ip + ';'  + str(routing_value) + ';' + str(state) + ';' + percurso + ';' + ficheiros
        return bytes(msg,'utf-8')

    def encodeGetRequest(self,content,ip_origem):
        msg = self.origin_ip + ';' + self.packet_type + ';' + content + ';' + ip_origem
        return bytes(msg,'utf-8')

    def encodeAliveMessage(self,ip_origem,ip_destino,percurso):
        msg = self.origin_ip + ';' + self.packet_type + ';' + ip_origem + ';' + ip_destino + ';' + percurso
        return bytes(msg,'utf-8')