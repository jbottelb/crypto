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
from MessageTypes import MessageTypes
from Utilities import Utilities

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 FullNode.py <port> [<trusted_hostname:port>]")
        exit(-1)
    
    port = int(sys.argv[1])
    trusted_host = None
    if len(sys.argv) == 3:
        trusted_host = sys.argv[2]
        try:
            trusted_host = trusted_host.split(":")
            trusted_host = (trusted_host[0], int(trusted_host[1]))
        except:
            print("Usage: python3 FullNode.py <port> [<trusted_hostname:port>]")
            exit(-1)
    
    # stores (hostname, port) pairs of other full nodes in the system
    neighbors = []

    #TODO: handle having a trusted host to start with (As a full node)
    if trusted_host is not None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        message = {"Type": MessageTypes.Get_Neighbors}
        rc = Utilities.sendMessage(sock, message)
        if rc:
            # sent message successfully to trusted node
            response = Utilities.readMessage(sock)
            if response is not None:
                neighbors = response.get("")

        # couldn't communicate with trusted node, fallback to seed nodes

        sock.close()


    # request seed nodes if we have no trusted host to start with
    active_seeds = None
    if trusted_host is None:
        active_seeds = Utilities.getActiveSeedNodes()
        if active_seeds is not None:
            print(f"Active seeds: {active_seeds}")
    
    main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_sock.bind(("", port))
    main_sock.listen()

    # dict of socket connections
    connections = {main_sock: f"localhost:{port}"}

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
                message = Utilities.readMessage(sock, connections)
                if message is not None:
                    handleMessage(message)
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

if __name__ == "__main__":
    main()

