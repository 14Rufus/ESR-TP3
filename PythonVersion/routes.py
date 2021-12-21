class RouteTable:
        
    def __init__(self):
        self.routes = {}

    def add_route(self,ip_origem,jump_distance):
        """
            routes = {
                ip_origem : {
                    metric : dis_to_server
                    state : 0 || 1
                }
            }
        """
        if ip_origem not in self.routes:
            info = {}
            info['metric'] = jump_distance
            info['state'] = 0
            self.routes[ip_origem]=info
        else:
            self.updateMetric(ip_origem, jump_distance)

    def setRouteActive(self,ip_origem):
        self.routes[ip_origem]['state'] = 1

    def getCurrentMetric(self,ip):
        return self.routes[ip]['metric']

    def updateMetric(self,ip,jump_distance):
        if self.routes[ip]['metric'] > jump_distance:
            self.routes[ip]['metric'] = jump_distance
    
    def getShortestRoute(self):
        minimum = 9999
        for ip in self.routes.keys():
            if v:=self.routes[ip]['metric'] < minimum:
                minimum=v
        return minimum
            