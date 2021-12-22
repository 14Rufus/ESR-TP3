class RouteTable:
        
    def __init__(self):
        self.routes = {}

    def add_route(self,ip_origem,jumps,state,route):
        """
            routes = {
                Exemplo tabela em R1
                ip_origem (R3) : {
                    previous_nodes: "ip_server"
                    jumps : 1
                    state : 0
                }
                ip_origem (R2) : {
                    previous_nodes : "ip_r3,ip_server"
                    jumps: 2
                    state : 0
                }

                Exemplo tabela em L1
                ip_origem (R1): {
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
            info['route'] = route
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