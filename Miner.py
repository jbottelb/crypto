#!/usr/bin/env python3
'''
Implementation of a miner
'''

from BlockChain import DIFFICULTY, Block
from hashlib import sha256
from Utilities import Utilities
import select
import sys
import socket
from MessageTypes import MessageTypes

N = 1000

class Miner:
    def __init__(self, pk):
        self.Node = None
        self.block = None
        self.pk = pk
        self.difficulty = DIFFICULTY

    # this is here for testing purposes
    def override_difficulty(self, d):
        self.difficulty = d   

    def run(self, URL):
        parent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            parent.connect(URL)
        except:
            print("Failed to connect to specified full node")
            parent.close()
            exit(-1)
        block = None
        hash = None
        mining = False
        while True:
            # check if there is a message from the Node
            readable, _, _ = select.select([parent], [], [], 60)
            # if so, deal with it
            if readable:
                res = Utilities.readMessage(parent)
                if res is None or res.get("Type", '') != MessageTypes.Send_Block:
                    continue
                try:
                    transactions = res.get("Transactions", [])
                    previous_hash = res.get("Prev_Hash", '')
                    block_index = res.get("Block_Index", -1)
                    block = Block(block_index, previous_hash, '')
                    for t in transactions:
                        block.add_transaction(t)
                except Exception as e:
                    print(e)
                    block = None
            elif hash:
                # send back block
                message = {"Type": "Send_Block", "Block_Index": block.index, "Prev_Hash": block.prev_hash,
                            "Nonce": block.nonce, "Hash": block.hash, "Transactions": block.transactions,
                            "Previous_Message_Recipients": []}
                Utilities.sendMessage(message, True, None, parent)
                mining = False
                block = None

            # if we recieved a block from the full node
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
                hash = self.mine(N)

    def mine(self, iterations=None):
        '''
        Finds an appropriate sha256 hash for a block

        Iterations: specifies the number of times we should mine for
        (useful if single-threaded and listening to parent)
        '''
        i = 0

        hash = sha256(str(self.block).encode()).hexdigest()
        while not hash.startswith(self.difficulty * "0"):
            # only mine a select number of times
            if iterations:
                i += 1
                if i >= iterations:
                    return None
            self.block.nonce += 1
            hash = sha256(str(self.block.string_for_mining()).encode()).hexdigest()
        self.block.hash = hash
        return hash

if __name__ == "__main__":
    _, pk, host, port = sys.argv
    URL = (host, port)
    miner = Miner(pk)
    miner.block = Block("0", "0", pk)
    miner.run(URL)
