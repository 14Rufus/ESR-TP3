import socket
import sys
import threading as t
from xml.dom import minidom
import time

HOST = socket.gethostbyname(socket.gethostname())  # Standard loopback interface address (localhost)
PORT = int(sys.argv[1])        # Port to listen on (non-privileged ports are > 1023)
CONFIG_FILE = sys.argv[2]

VIZINHOS = {}
routers = set()

def read_config_file():
    xmldoc = minidom.parse(CONFIG_FILE)
    router_tag = xmldoc.getElementsByTagName('router')
    for r in router_tag:
        name_tag = r.getElementsByTagName('router_name')
        name = name_tag[0].attributes['name'].value
        vizinhos_tag = r.getElementsByTagName('router_ip')
        vizinhos = []
        for v in vizinhos_tag:
            vizinhos.append(v.attributes['ip'].value)
        VIZINHOS[name] = vizinhos

def new_client(client_socket,addr):
    while True:
        data = client_socket.recv(1024)
        msg = data.decode('utf-8')
        #print('Connected by', addr)
        if not data:
            break
        elif "NEIGHBOURS" in msg:
            host = socket.gethostbyaddr(addr[0])
            routers.add(host[0])
            for viz in VIZINHOS[host[0]]:
                client_socket.sendall(bytes(f"NEIGHBOUR:{viz}",'utf-8'))
                time.sleep(1)
        elif "BEACON" in msg:
            if host:=socket.gethostbyaddr(addr[0]) in routers:
                client_socket.sendall(bytes("Confirmed Alive",'utf-8'))
            else:
                client_socket.sendall(bytes("Added to router list",'utf-8'))
                routers.add(host[0])
        else:
            print(msg)
        client_socket.sendall(bytes(f"Connected to server at {HOST}",'utf-8'))
    client_socket.close()


threads = []

read_config_file()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #stream = tcp    dgram = udp  inet = ipv4
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        print('NEW CLIENT CONNECTION')
        new_c_thread = t.Thread(target=new_client,args=(conn,addr))
        threads.append(new_c_thread)
        new_c_thread.start()
        new_c_thread.join()