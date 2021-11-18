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

BUF_SIZE = 10000




def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 FullNode.py <port> [<trusted_hostname:port>]")
        exit(-1)
    
    port = int(sys.argv[1])
    
    main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_sock.bind(("", port))
    main_sock.listen()
    
    connections = {main_sock}
    # neighbors = []

    while 1:
        # listen for a second for a readable socket
        readable, writeable, exceptional = select.select(connections, [], [], 1)
        for sock in readable:
            # main socket has bytes to read, means we should accept 
            # an incoming connection and store a socket for it
            if sock == main_sock:
                conn, addr = sock.accept()
                connections.add(conn)
                print(f"Received ping from : {addr}")
            # otherwise, we have a client making a request or closing
            # a connection
            else:
                # read from the socket
                try:
                    data = sock.recv(BUF_SIZE)
                except ConnectionResetError:
                    # don't exit if client ends connection,
                    # just remove the connection from the dict
                    sock.close()
                    connections.discard(sock)
                    continue
                if not data:
                    # client may have ended the connection
                    sock.close()
                    connections.discard(sock)
                    continue

                # TODO: handle request from socket

        # handle any issues with sockets
        for sock in exceptional:
            if sock == main_sock:
                # issue with main socket, exit node
                main_sock.close()
                exit(-1)
            else:
                # issue with a client connection socket,
                # remove it from the dict
                try:
                    sock.close()
                except:
                    pass
                connections.discard(sock)

if __name__ == "__main__":
    main()

