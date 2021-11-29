'''
Brad Budden and Josh Bottelberghe
Distributed Systems - Final Project
NameServer.py

Description: This program maintain a list of the 
active seed nodes in the network by pinging them
at a specified interval. Nodes hoping to join the system 
can reach out to this name server for the names of these
seed nodes. Since we are running the seed nodes
ourselves, we trust them to behave correctly. Incoming
nodes do have the option of identifying other
nodes in the system to connect to without the use
of the name server or seed nodes. Listens on a specified port.
'''

import sys
import socket
import time
import select
import re
import json

from MessageTypes import MessageTypes
BUF_SIZE = 10000

active_seeds = set()
possible_seeds = set()
#[("student11.cse.nd.edu", 12001), ("student12.cse.nd.edu", 12000)]

# returns a string 
def get_active_seeds_response_json():
    return json.dumps({"Type": "Get_Seed_Nodes_Response", "Active Seeds": list(active_seeds)})

def ping_seed_nodes():
    for ps in possible_seeds:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # see if seed node is running
            sock.connect(ps)
            # yes -> add to active seeds
            active_seeds.add(ps)
            print(f"Successful ping to {ps}")
            sock.close()
        except:
            # no -> remove from active seeds
            active_seeds.discard(ps)       
            

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 NameServer.py <port> <ping_interval>")
        exit(-1)
    
    name_server_port = int(sys.argv[1])
    ping_interval = sys.argv[2]

    # read in possible seed nodes from text file containing seed node names
    with open("SeedNodesList.txt") as fd:
        for line in fd.readlines():
            format = re.compile("^.*:[0-9]*$")
            if not format.match(line):
                # exit server if we cannot read the seed nodes text file
                print("Invalid format of seed nodes text file. Use one line per seed node and format as <hostname>:<port>")
                exit(-1)
            line = line.split(":")
            possible_seeds.add((line[0], int(line[1])))
    
    # create main socket to listen for connections
    main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_sock.bind(("", name_server_port))
    main_sock.listen()
    
    # dict of socket connections
    connections = {main_sock: f"localhost:{name_server_port}"}
    first_ping = True
    latest_ping = time.time()

    while 1:
        if int(time.time() - latest_ping) > int(ping_interval) or first_ping:
            ping_seed_nodes()
            first_ping = False
            latest_ping = time.time()  
              
        # listen for a second for a readable socket
        readable, writeable, exceptional = select.select(connections.keys(), [], [], 1)
        for sock in readable:
            # main socket has bytes to read, means we should accept 
            # an incoming connection and store a socket for it
            if sock == main_sock:
                conn, addr = sock.accept()
                connections[conn] = f"{addr[0]}:{addr[1]}"
                print(f"New connection from : {addr}")
            # otherwise, we have a client making a request or closing
            # a connection
            else:
                # read from the socket
                print(f"New request from : {connections[sock]}")
                try:
                    data = sock.recv(BUF_SIZE)
                except ConnectionResetError:
                    # don't exit if client ends connection,
                    # just remove the connection from the dict
                    print("ConnectionResetError")
                    sock.close()
                    del connections[sock]
                    continue
                if not data:
                    # client may have ended the connection
                    sock.close()
                    del connections[sock]
                    continue

                # TODO: handle request from socket
                try:
                    data = str(data, 'utf-8')
                    request = json.loads(data)
                except Exception as e:
                    # improperly formatted request for seed node addresses
                    print("Improper Request Format")
                    sock.close()
                    del connections[sock]
                    continue
                print(f"Handling request from {connections[sock]}...")
                if request.get("Type", 0) == MessageTypes.Get_Seed_Nodes:
                    # appropriate request, return list of seed nodes
                    responseString = get_active_seeds_response_json()
                    responseBytes = bytearray(responseString.encode('utf-8'))
                    sock.sendall(responseBytes)
                    # clean up connection immediately
                    sock.close()
                    del connections[sock]
                else:
                    # improperly formatted request for seed node addresses
                    sock.close()
                    del connections[sock]
                    continue

        # handle any issues with sockets
        for sock in exceptional:
            if sock == main_sock:
                # issue with main socket, delete it
                del connections[sock]
                main_sock.close()
                try:
                    # try to create a new one
                    main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    main_sock.bind(("", name_server_port))
                    main_sock.listen()
                    connections[main_sock] = f"localhost:{name_server_port}"
                except:
                    # exit name server because we cannot create a new main socket
                    exit(-1)
            else:
                # issue with a client connection socket,
                # remove it from the dict
                try:
                    sock.close()
                except:
                    pass
                del connections[sock]
    


if __name__ == "__main__":
    main()