#!/usr/bin/env python3
'''
Implementation of a miner node
'''

import Constants
from BlockChain import Block
from hashlib import sha256
from Messaging import Messaging
import select
import sys
import socket
from MessageTypes import MessageTypes
import random

N = 500000 # determines number of nonce values to test before
          # pausing mining to listen for new messages

class Miner:
    def __init__(self, pk):
        self.Node = None
        self.block = None
        self.pk = pk
        self.difficulty = Constants.DIFFICULTY

    # this is here for testing purposes
    def override_difficulty(self, d):
        self.difficulty = d

    # connect to the provided full node
    def join_as_miner(self, parent: socket.socket):
        '''
        Attempts to join the full node as a miner.
        Returns: 1 if successful, 0 otherwise
        '''
        message = {"Type": MessageTypes.Join_As_Miner}
        Messaging.sendMessage(message, True, sock=parent)
        parent.settimeout(5)
        response = Messaging.readMessage(parent)
        if response is not None:
            if response.get("Type", 0) != MessageTypes.Join_As_Miner_Response or response.get("Decision", '') != "Yes":
                print("Should have gotten an affirmative join as miner response")
                return 0
        return 1


    def run(self, full_node_addr: tuple):
        parent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        parent.connect(full_node_addr)
        try:
            rc = self.join_as_miner(parent)
            if rc == 0:
                # issue connecting to full node as miner
                parent.close()
                exit(-1)
        except Exception as e:
            print(e)
            print("Failed to connect to specified full node")
            parent.close()
            exit(-1)
        block = None
        hash = None
        mining = False
        while True:
            # check if there is a message from the Node
            readable, _, _ = select.select([parent], [], [], 0.05)
            # if so, deal with it
            if readable:
                res = Messaging.readMessage(parent)
                if res is None or res.get("Type", '') != MessageTypes.Start_New_Block:
                    continue
                try:
                    transactions = res.get("Transactions", [])
                    previous_hash = res.get("Prev_Hash", '')
                    block_index = res.get("Block_Index", -1)
                    block = Block(block_index, previous_hash, '')
                    for t in transactions:
                        block.add_transaction(Messaging.transactionDictToObject(t))
                except Exception as e:
                    print(e)
                    block = None
            elif hash:
                # We found a hash before receiving a new block to mine; send back block
                message = {"Type": MessageTypes.Send_Block, "Block_Index": block.index, "Miner_PK": self.pk,
                            "Prev_Hash": block.prev_hash, "Nonce": block.nonce, "Hash": hash,
                            "Transactions": [txn.to_json() for txn in block.transactions], "Previous_Message_Recipients": []}
                print(f"Message from miner to parent full node after finding a block: \n{message}")
                Messaging.sendMessage(message, True, None, parent)
                mining = False
                block = None

            # if we recieved a block from the full node, update our personal
            # block object (which we will convert to a string to mine on)
            if block:
                hash = None
                mining = True
                self.block.index = block.index
                self.block.transactions = block.transactions
                self.block.prev_hash = block.prev_hash
                self.block.nonce = block.nonce
                self.block.hash = None
            else:
                mining = False

            # if we are mining, mine for a bit
            if mining and block:
                print("starting to mine")
                hash = self.mine(N)

    def mine(self, iterations=None):
        '''
        Finds an appropriate sha256 hash for a block

        Iterations: specifies the number of nonce values to try before listening
        for new messages from the parent full node
        (useful if single-threaded and listening to parent)
        '''
        i = 0

        self.block.nonce = random.randint(0, Constants.DIFFICULTY * 100000000)

        hash = sha256(self.block.string_for_mining().encode()).hexdigest()
        while not hash.startswith(self.difficulty * "0"):
            # only mine a select number of times
            if iterations:
                i += 1
                if i >= iterations:
                    return None
            self.block.nonce += 1
            hash = sha256(self.block.string_for_mining().encode()).hexdigest()
        self.block.hash = hash
        return hash

    @staticmethod
    def decorate_miner_public_key(miner_pk):
        beginning = "-----BEGIN PUBLIC KEY-----"
        ending = "-----END PUBLIC KEY-----"
        return beginning + miner_pk + ending

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 Miner.py <Miner public key> <Full node host> <Full node port>")
    miner_pk = Miner.decorate_miner_public_key(sys.argv[1])
    host = sys.argv[2]
    port = sys.argv[3]
    full_node_addr = (host, int(port))
    miner = Miner(miner_pk)
    miner.block = Block("0", "0", miner_pk)
    miner.run(full_node_addr)
