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

    def connect_to_node(self, URL):
        '''
        Returns node to mine for
        '''
        Utilities.sendMessage()

        pass

    def run(self, URL):
        parent = self.connect_to_node(URL)
        block = None
        hash = None
        mining = False
        while True:
            # check if there is a message from the Node
            readable, _, _ = select.select([parent], [], [], 60)
            # if so, deal with it
            if readable:
                res = Utilities.readMessage(parent)
                try:
                    block = Block(res["index"], res["prev_hash"], res["pk"])
                    for t in res["transactions"]:
                        block.add_transaction(t)
                except Exception as e:
                    print(e)
                    block = None
            elif hash:
                # send back block
                Utilities.sendMessage(dict(self.block), True, None, parent)

            # if mining status should change (enough transactions)
            if block:
                mining = True
                self.block.index = block.index
                self.block.transactions = block.transactions
                self.prev_hash = block.prev_hash
            else:
                mining = False

            # if we are mining, mine for a bit
            if mining and block:
                hash = self.mine(block, N)

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
            hash = sha256(str(block.string_for_mining()).encode()).hexdigest()
        self.block.hash = hash
        return hash

if __name__ == "__main__":
    _, pk, host, port = sys.argv
    URL = (host, port)
    miner.block = Block("0", "0", pk)
    miner = Miner(pk)
    miner.run(URL)
