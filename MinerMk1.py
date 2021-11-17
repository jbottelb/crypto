#!/usr/bin/env python3
'''
Implimentation of a miner
'''

from "../Modules/BlockChain.py" import Block
from hashlib import sha256

class Miner:
    def __init__(self):
        self.block = None

    def mine(self):
        hash = None

        while not hash.startswith(Block.DIFFICULTY * "0"):
            hash = sha256(str(self.block))
            self.block.nonce += 1

if __name__ == "__main__":
    miner = Miner()
    b = Block(0, 0, 0)

    for i in range(5):
        Block.add_transaction("random transcation, text wont matter")

    print(b)
