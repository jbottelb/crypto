#!/usr/bin/env python3
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
Reads list of seed nodes to ping from a file named 
"SeedNodesList.txt"
'''

import sys
import socket
import time
import select
import re
import json

from MessageTypes import MessageTypes
from Constants import Constants
from Messaging import Messaging

active_seeds = set()
possible_seeds = set()

# returns a string 
def getActiveSeedsResponseDict():
    return {"Type": "Get_Seed_Nodes_Response", "Nodes": list(active_seeds)}

def pingSeedNodes():
    for ps in possible_seeds:
        if Messaging.pingNode(ps):
            # yes -> add to active seeds
            active_seeds.add(ps)
        else:
            # no -> remove from active seeds
            active_seeds.discard(ps)            

'''
Handle messages that request a list of seed nodes. Ignore other message types.
Removes sockets after handling the message.
Returns: nothing
'''
def handleMessage(sock: socket.socket, message: dict, connections: dict):
    if message.get("Type", 0) == MessageTypes.Get_Seed_Nodes:
        # appropriate request, return list of seed nodes
        responsedict = getActiveSeedsResponseDict()
        rc = Messaging.sendMessage(responsedict, False, sock=sock, connections=connections)
    else:
        # improperly formatted request for seed node addresses
        sock.close()
        del connections[sock]

'''
Send our name server's information to catalog.cse.nd.edu.
Returns: nothing
'''
def updateCatalog(port: int, project_name: str) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    body = {
        "type": "nameserver",
        "owner": "bbudden",
        "port": port,
        "project": project_name
    }
    body = json.dumps(body)
    sock.sendto(bytes(body, "utf-8"), (Constants.CATALOG_ENDPOINT, Constants.CATALOG_PORT))
            

def main():
    if len(sys.argv) != 3:
        print("Usage: NameServer.py <port> <ping_interval>")
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
    first_catalog_update = True
    latest_catalog_update = time.time()

    while 1:
        # ping seed nodes at the specified interval to determine which are active
        if int(time.time() - latest_ping) > int(ping_interval) or first_ping:
            pingSeedNodes()
            first_ping = False
            latest_ping = time.time() 

        # update catalog server at a predetermined interval
        if int(time.time() - latest_catalog_update) > Constants.CATALOG_UPDATE_INTERVAL or first_catalog_update:
            print(f"Sending keep-alive at {time.time()}")
            updateCatalog(name_server_port, Constants.PROJECT_NAME)
            first_catalog_update = False
            latest_catalog_update = time.time()
              
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
                message = Messaging.readMessage(sock, connections)
                if message is None:
                    continue
                else:
                    print(f"Handling request from {connections[sock]}...")
                    handleMessage(sock, message, connections)

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