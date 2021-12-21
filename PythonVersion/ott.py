import sys
from server import Server
from node import Node

if '-s' in sys.argv:
    sys.argv.remove('-s')
    server = Server()
    server.start(sys.argv[1:])
else:
    node = Node()
    node.start(sys.argv[1:])
