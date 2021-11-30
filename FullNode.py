'''
Brad Budden and Josh Bottelberghe
Distributed Systems - Final Project
FullNode.py

Description: This program will implement
behavior consistent with the protocols
expected from a full node in our system.
'''

# TODO: implement connection to either name server or trusted_hostname:port

# import Node

import socket
import sys
import select
import json
from MessageTypes import MessageTypes
import time
from Utilities import Utilities
from Constants import Constants

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 FullNode.py <port> [<trusted_hostname:port>]")
        exit(-1)
    
    port = int(sys.argv[1])

    start_time = time.time()
    
    main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_sock.bind(("", port))
    main_sock.listen()
    
    # dict of socket connections
    connections = {main_sock: f"localhost:{port}"}
    # neighbors = []

    while 1:
        # listen for a second for a readable socket
        readable, writeable, exceptional = select.select(connections.keys(), [], [], 1)
        for sock in readable:
            # main socket has bytes to read, means we should accept 
            # an incoming connection and store a socket for it
            if sock == main_sock:
                conn, addr = sock.accept()
                connections[conn] = f"{addr[0]}:{addr[1]}"
                print(f"Received ping from : {addr}")
            # otherwise, we have another node making a request or closing
            # a connection
            else:
                # read from the socket
                try:
                    data = sock.recv(Constants.BUF_SIZE)
                except ConnectionResetError:
                    # don't exit if client ends connection,
                    # just remove the connection from the dict
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
                    # improperly formatted request
                    sock.close()
                    del connections[sock]
                    continue
                print(f"Handling message from {connections[sock]}...")
                if request.get("Type", 0) == MessageTypes.Get_Seed_Nodes_Response:
                    response = request.get("Nodes", 0)
                    if response == 0:
                        print("No Seed Nodes Returned by Name Server. Provide a trusted full node in command line args or try again later.")
                        exit(-1)
                    print(response)
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
                    main_sock.bind(("", port))
                    main_sock.listen()
                    connections[main_sock] = f"localhost:{port}"
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
        
        # request seed nodes
        if time.time() - start_time > 10:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            requestSeedNodes(sock)
            data = sock.recv(Constants.BUF_SIZE)
            response = Utilities.readMessage(data)
            print(response)

if __name__ == "__main__":
    main()

