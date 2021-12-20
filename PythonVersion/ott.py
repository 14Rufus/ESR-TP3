import sys
from server import Server
from node import Node

if '-s' in sys.argv:
    sys.argv.remove('-s')
    server = Server()
    print(sys.argv[1:])
    server.start(sys.argv[1:])
else:
    node = Node()
    node.start(sys.argv[1:])
