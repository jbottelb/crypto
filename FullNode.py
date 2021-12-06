#!/usr/bin/env python3
'''
Brad Budden and Josh Bottelberghe
Distributed Systems - Final Project
FullNode.py

Description: This program will implement
behavior consistent with the protocols
expected from a full node in our system.
'''

import socket
import sys
import select
from MessageTypes import MessageTypes
from Utilities import Utilities
import BlockChain
import time
from Constants import Constants

### TODO: TESTING ######
START_TIME = {"start_time": 0}
FIRST_MINER = {"first": True}
FIRST_FINISHED = {"first": True}
TRANSACTIONS = [{"test": "This is transaction 1 data"}, {"test": "This is transaction 2 data"}, {"test": "This is transaction 3 data"}]
#####################33

def handle_message(sock: socket.socket, message: dict, neighbors: set, miners: set, 
                  blockchain: BlockChain.BlockChain, connections: dict):
    '''
    Handles behavior for different message types that a full node
    expects to receive. Ignores messages that are irrelevant to
    full nodes.
    Returns: nothing
    '''
    msgtype = message.get("Type", 0)
    if not msgtype:
        return
    if msgtype == MessageTypes.Get_Neighbors:
        response = {"Type": MessageTypes.Get_Neighbors_Response, "Neighbors": neighbors}
        # send our neighbors to the full node that is requesting them
        Utilities.sendMessage(response, False, sock=sock, connections=connections)
    elif msgtype == MessageTypes.Get_Neighbors_Response:
        for neigh in message.get("Neighbors", []):
            neighbors.add(tuple(neigh))
    elif msgtype == MessageTypes.Join_As_Miner:
        # Other implementations of full nodes could check if this miner
        # belongs to some list of miner processes that it wants to trust/use.
        # We will default to accepting new miners that want to work for us.
        response = {"Type": MessageTypes.Join_As_Miner_Response, "Decision": "Yes"}
        miner_addr = connections[sock].split(":")
        miner_addr_tuple = (miner_addr[0], int(miner_addr[1]))
        miners.add(miner_addr_tuple)
        # send decision to miner so it knows we accepted it and will send
        # tasks its way soon; keep socket open and save it
        Utilities.sendMessage(response, True, sock=sock, connections=connections)

        # #############TODO: edit this after testing
        start_new_block_message = {"Type": MessageTypes.Start_New_Block, "Transactions": TRANSACTIONS,
                                    "Prev_Hash": "12345", "Block_Index": 10}
        Utilities.sendMessage(start_new_block_message, True, sock=sock, connections=connections)
        ##### TODO: TESTING ######
        if FIRST_MINER["first"]:
            START_TIME["start_time"] = time.time()
            FIRST_MINER["first"] = False
        ####################
        ################

    elif msgtype == MessageTypes.Send_Block:
        # TODO: HANDLE THE ACCEPTANCE (In real implementation, this will need to check if its coming from miner)
        print(f"Miner {connections[sock]} found block after {time.time() - START_TIME['start_time']} seconds")
        # if FIRST_FINISHED["first"]:
        #     FIRST_FINISHED["first"] = False
    
    
    
    else:
        pass

    # TODO: Implement handling of other messages that a full node should expect.
    #       Right now, we are only handling messages needed to talk with miners.


def ping_nodes(nodes: set):
    '''
    Pings the nodes specified in the provided set. If they aren't alive,
    removes them from the set.
    '''
    for node in nodes:
        rc = Utilities.pingNode(node)
        if not rc:
            nodes.discard(node)

def main():

    if len(sys.argv) < 2 or len(sys.argv) > 4:
        print("Usage: FullNode.py <port> [<trusted_hostname:port>]\n'-s' option to force seed behavior (i.e., generate a genesis block")
        exit(-1)
    
    port = int(sys.argv[1])
    trusted_host = None
    if len(sys.argv) == 3:
        # read in and store trusted host
        trusted_host = sys.argv[2]
        try:
            trusted_host = trusted_host.split(":")
            trusted_host = (trusted_host[0], int(trusted_host[1]))
        except:
            print("Usage: FullNode.py <port> [<trusted_hostname:port>]")
            exit(-1)
    
    # stores (hostname, port) pairs of other full nodes in the system
    neighbors = set()
    # stores (hostname, port) paris of miners that are working for it
    miners = set()
    # set of pending transactions (i.e., not yet added to blockchain)
    pending_transactions = set()
    # personal copy of longest blockchain
    blockchain = BlockChain.BlockChain()
    # create a genesis block if this node is to act as a seed node
    if "-s" in sys.argv:
        blockchain.create_genesis()

    # handle having a trusted host to start with (As a full node)
    if trusted_host is not None:
        new_neighbors = Utilities.getNeighbors(trusted_host)
        if new_neighbors is not None:
            neighbors = set([tuple(node) for node in new_neighbors])
            neighbors.add(trusted_host)
        # fallback to seed nodes if needed
        elif new_neighbors is None or len(neighbors) == 1:
            active_seeds = Utilities.getActiveSeedNodes()
            if active_seeds is not None:
                for node in active_seeds:
                    neighbors.add(tuple(node))
                # also get neighbors of the seed nodes
                for node in active_seeds:
                    new_neighbors = Utilities.getNeighbors(node)
                    if new_neighbors is not None:
                        for nn in new_neighbors:
                            neighbors.add(tuple(nn))
    else:
        # request seed nodes if we have no trusted host to start with
        active_seeds = None
        active_seeds = Utilities.getActiveSeedNodes()
        if active_seeds is not None:
            neighbors = set([tuple(node) for node in active_seeds])
            # also get neighbors of the seed nodes
            for node in active_seeds:
                new_neighbors = Utilities.getNeighbors(node)
                if new_neighbors is not None:
                    for nn in new_neighbors:
                        neighbors.add(tuple(nn))

    # handle case where we found no neighbors
    if len(neighbors) == 0:
        print("No active full nodes discovered")
        exit(-1)

    # TODO: print(neighbors)
    
    main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_sock.bind(("", port))
    main_sock.listen()

    # dict of socket connections
    connections = {main_sock: f"localhost:{port}"}

    first_ping = True
    latest_ping = time.time()

    while 1:
        # ping neighbor and miner nodes at the specified interval to determine which are active
        if int(time.time() - latest_ping) > int(Constants.NEIGHBOR_PING_INTERVAL) or first_ping:
            # remove nodes from the sets if they aren't active anymore
            ping_nodes(neighbors)
            ping_nodes(miners)
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
                # add never before seen nodes to neighbors
                neighbors.add(addr)
                # TODO: print(f"Received ping from : {addr}")
            # otherwise, we have another node making a request or closing
            # a connection
            else:
                # read from the socket
                message = Utilities.readMessage(sock, connections)
                if message is not None:
                    handle_message(sock, message, neighbors, miners, blockchain, connections)
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
        
        # TODO: update pending_transactions pool if a block was found and send
        #       new start_new_block message to miners

if __name__ == "__main__":
    main()

