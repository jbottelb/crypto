#!/usr/bin/env python3

'''
Module for nodes in the system.
Includes functions for keeping track and communicating with other nodes.
'''

# transactions per block
TPB = 5
# number of leading zeros on computed hashed
DIFFICULTY = 2
# reward for mining Block
COINBASE = 10

class BlockChain:
    def __init__(self):
        pass

    def create_genesis():
        pass

class Block:
    def __init__(self, index, prev_hash, pk):
        self.index = index
        self.prev_hash = prev_hash
        self.miner_pk = pk
        self.nonce = 0

        self.transactions = 0
        self.hash = None

    def add_transaction(transaction):
        self.transactions.append(transaction)

    def __str__(self):
        block_str = ""
        block_str += "Block index: " + self.index + "\n"
        block_str += "Prev Hash: " + self.prev_hash + "\n"
        block_str += "Nonce: " + self.nonce + "\n"
        block_str += "Coinbase: " + self.miner_pk + " " + str(COINBASE) + "\n"
        for t in self.transactions:
            block_str += str(t) + "\n"
        if self.hash:
            block_str += self.hash
        return block_str
