class RouteTable:
        
    def __init__(self):
        self.routes = {}

    def add_route(self,ip_origem,jumps,state,route,server_ip,contents):
        """
            routes = {
                Exemplo tabela em R1
                ip_origem (R3) : {
                    server : ip_server
                    files : "file1.txt,file2.txt"
                    previous_nodes: "ip_r3,ip_server"
                    jumps : 1
                    state : 0
                }
                ip_origem (R2) : {
                    server : ip_server
                    files : "file1.txt,file2.txt"
                    previous_nodes : "ip_r3,ip_server"
                    jumps: 2
                    state : 0
                }

                Exemplo tabela em L1
                ip_origem (R1): {
                    server : ip_server
                    files : "file1.txt,file2.txt"
                    previous_nodes : "ip_r1,ip_r3,ip_server"
                    jumps: 3
                    state : 0
                }
            }
        """
        if ip_origem not in self.routes:
            info = {}
            info['jumps'] = jumps
            info['state'] = state
            info['route'] = route.split(',')
            info['server_ip'] = server_ip
            info['files'] = contents.split(',')
            self.routes[ip_origem]=info
        else:
            self.updateMetric(ip_origem, jumps)

    def setRouteActive(self,ip_origem):
        self.routes[ip_origem]['state'] = 1

    def getJumps(self,ip):
        return self.routes[ip]['jumps']
    
    def getState(self,ip):
        return self.routes[ip]['state']

    def getPercurso(self,ip):
        return self.routes[ip]['route']
    
    def getServerAddress(self,ip):
        return self.routes[ip]['server_ip']
    
    def getFilesAvaiable(self,ip):
        return self.routes[ip]['files']

    def updateJumpDistance(self,ip,jump_distance):
        if self.routes[ip]['jumps'] > jump_distance:
            self.routes[ip]['jumps'] = jump_distance
    
    def getShortestRoute(self):
        minimum = 9999
        selected = None
        for ip in self.routes.keys():
            if (v:=self.routes[ip]['jumps']) < minimum:
                minimum = v
                selected = ip
        return selected
            
    def existsRoute(self,ip):
        return self.routes.get(ip, 'None')
    
    def getTable(self):
        return self.routes

    def updateOnNeighbourShutdown(self,origin_ip):
        self.routes.pop(origin_ip)