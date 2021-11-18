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
BUF_SIZE = 10000

active_seeds = set()
possible_seeds = [("student11.cse.nd.edu", 12001), ("student12.cse.nd.edu", 12000)]

def return_active_seeds():
    return_dict = {"Length": 0, "Active Seeds": []}
    for active_seed in active_seeds:
        return_dict["Active Seeds"].append(active_seed[0] + ":" + str(active_seed[1]))
    return str(return_dict)

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
    
    main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_sock.bind(("", name_server_port))
    main_sock.listen()
    
    connections = {main_sock}
    first_ping = True
    latest_ping = time.time()

    while 1:
        if int(time.time() - latest_ping) > int(ping_interval) or first_ping:
            ping_seed_nodes()
            first_ping = False
            latest_ping = time.time()  
              
        # listen for a second for a readable socket
        readable, writeable, exceptional = select.select(connections, [], [], 1)
        for sock in readable:
            # main socket has bytes to read, means we should accept 
            # an incoming connection and store a socket for it
            if sock == main_sock:
                conn, addr = sock.accept()
                connections.add(conn)
                print(f"New connection from : {addr}")
                responseString = return_active_seeds()
                responseBytes = bytearray(responseString.encode('utf-8'))
                conn.sendall(responseBytes)
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