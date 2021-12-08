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
from BlockChain import BlockChain, Block
import time
from Constants import Constants
from BlockChainCollection import BlockChainCollection


def handle_message(sock: socket.socket, message: dict, neighbors: set, miners: set,
                  blockchains_collection: BlockChainCollection, connections: dict,
                  orphan_blocks: set, pending_transactions: set, block_hashes_seen_before: set):
    '''
    Handles behavior for different message types that a full node
    expects to receive. Ignores messages that are irrelevant to
    full nodes. May update neighbors, miners, blockchain, and connections.
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
    elif msgtype == MessageTypes.Send_Block:
        hash = message["Hash"]
        if hash in block_hashes_seen_before:
            # prevents us from dealing with blocks that we've already handled before
            return
        else:
            block_hashes_seen_before.add(hash)
        transactions = [Utilities.transactionDictToObject(txn) for txn in message["Transactions"]]
        new_block = Block(message["Block_Index"], message["Prev_Hash"], message["Miner_PK"],
                          message["Nonce"], transactions, message["Hash"])
        if sock.getpeername() in miners:
            # Block came from miner. If all transactions included in the block are still in
            # pending_transactions, then we know that this miner is our first miner to solve the hash,
            # and so we should forward the block (after adding it). If any transactions in the block
            # aren't in pending_transactions, then we've either gotten a valid block from another full node
            # with some of the transactions included already, OR another one of our miners already
            # mined a block with some of those transactions, and so we should discard the block.
            for txn in transactions:
                if txn not in pending_transactions:
                    return
            # Try to add it if valid
            rc = blockchains_collection.try_add_block(new_block, orphan_blocks, pending_transactions)
            if rc == 1:
                # block is in our main blockchain fork, forward block to neighbors
                message["Previous_Message_Recipients"] = [sock.getsockname()]
                for n in neighbors:
                    Utilities.sendMessage(message, addr=n)
        else:
            # Otherwise, the block is coming from a full node. Try to add it to a blockchain fork.
            rc = blockchains_collection.try_add_block(new_block, orphan_blocks, pending_transactions)
            if rc == 1 or rc == 3:
                # block is in our main blockchain fork, forward block to neigbors
                message["Previous_Message_Recipients"].append(sock.getsockname())
                for n in neighbors:
                    Utilities.sendMessage(message, addr=n)
            elif rc == 0:
                # block was an orphan, try to get its parent from our neighbors
                message = {"Type": MessageTypes.Get_Block, "Hash": new_block.hash}
                for n in neighbors:
                    Utilities.sendMessage(message, addr=n)
    elif msgtype == MessageTypes.Get_Block:
        desired_block_hash = message["Hash"]
        # try to find the block in our blockchains collection
        block = blockchains_collection.get_block_by_hash(desired_block_hash, orphan_blocks)
        if block:
            # send the block to the requesting full node
            message = {"Type": MessageTypes.Send_Block, "Block_Index": block.index,
                       "Miner_PK": block.miner_pk, "Prev_Hash": block.prev_hash,
                       "Nonce": block.nonce, "Hash": block.hash, "Transactions": block.transactions,
                       "Previous_Message_Recipients": []}
            Utilities.sendMessage(message, sock=sock)

    # elif msgtype == MessageTypes.

    # get_blockchain

    # get_blockchain_response

    # send_transaction

    # send_transaction_response



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

    if len(sys.argv) < 2 or len(sys.argv) > 5:
        print("Usage: FullNode.py <port> [--trusted <trusted_hostname:port> <--seed>]\n 'seed' forces seed behavior (i.e., generates a genesis block")
        exit(-1)

    if len(sys.argv) == 3:
        if sys.argv[2] != "--seed":
            print("Usage: FullNode.py <port> [--trusted <trusted_hostname:port> | <--seed>]\n 'seed' forces seed behavior (i.e., generates a genesis block")

    port = int(sys.argv[1])
    trusted_host = None
    if "--trusted" in sys.argv:
        # read in and store trusted host
        try:
            trusted_host = sys.argv[3]
            trusted_host = trusted_host.split(":")
            trusted_host = (trusted_host[0], int(trusted_host[1]))
        except:
            print("Usage: FullNode.py <port> [--trusted <trusted_hostname:port> | <--seed>]\n 'seed' forces seed behavior (i.e., generates a genesis block")
            exit(-1)

    # stores (hostname, port) pairs of other full nodes in the system
    neighbors = set()
    # stores (hostname, port) paris of miners that are working for it
    miners = set()
    # set of pending transactions (i.e., not yet added to blockchain)
    pending_transactions = set()
    # create set of orphan blocks
    orphan_blocks = set()
    # create set of block hashes that we have seen before
    block_hashes_seen_before = set()

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

    # TODO: print(neighbors)

    # The blockchains_collection will hold multiple forks of the blockchain
    # (if needed) and abstract the appending of blocks
    blockchains_collection = BlockChainCollection()
    # create a blockchain and a genesis block if this node is to act as a seed node
    if "--seed" or "-s" in sys.argv:
        # create personal copy of longest blockchain (more may be stored later);
        # note that this blockchain fork will generate its own genesis block because
        # no data is passed in
        bc = BlockChain()
        blockchains_collection.add_blockchain_fork(bc)
    else:
        # otherwise, get blockchains from neighbors and make the longest
        # one our active fork (also store other forks of equal length)
        longest_bc_length = 0
        longest_bc = None
        tied_length_blockchains = []
        for n in neighbors:
            # TODO: check if this is working
            bc = Utilities.getBlockchain(n)
            if not bc:
                continue
            if len(bc.block_chain) > longest_bc:
                # found a new longest fork, store this one for now
                longest_bc = bc
                longest_bc = bc.length
            elif len(bc.block_chain) == longest_bc:
                # found a fork with same length as current longest
                # fork, store it as well
                tied_length_blockchains.append(bc)
        blockchains_collection.add_blockchain_fork(longest_bc)
        # store all the longest blockchain forks in our blockchain collection
        for tlbc in tied_length_blockchains:
            # the longest blockchain could have changed, so check lengths again
            if tlbc.length == longest_bc_length:
                blockchains_collection.add_blockchain_fork(tlbc)

    # TODO:
    blockchains_collection.print_forks()

    main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_sock.bind(("", port))
    main_sock.listen()

    # dict of socket connections
    connections = {main_sock: f"localhost:{port}"}

    first_ping = True
    latest_ping = time.time()
    latest_prune = time.time()

    while 1:
        # ping neighbor and miner nodes at the specified interval to determine which are active
        if int(time.time() - latest_ping) > int(Constants.NEIGHBOR_PING_INTERVAL) or first_ping:
            # remove nodes from the sets if they aren't active anymore
            ping_nodes(neighbors)
            ping_nodes(miners)
            first_ping = False
            latest_ping = time.time()

        # prune the blockchain collection so that short forks are discarded
        if int(time.time() - latest_prune) > int(Constants.BLOCKCHAIN_FORK_PRUNING_INTERVAL):
            blockchains_collection.prune_short_forks()

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
            # otherwise, we have another node making a request or closing
            # a connection
            else:
                # read from the socket
                message = Utilities.readMessage(sock, connections)
                if message is not None:
                    handle_message(sock, message, neighbors, miners, blockchains_collection,
                                   connections, orphan_blocks, pending_transactions, block_hashes_seen_before)
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
