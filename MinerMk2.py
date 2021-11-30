#!/usr/bin/env python3
'''
Implementation of a miner
'''

from BlockChain import DIFFICULTY, Block
from hashlib import sha256

class Miner:
    def __init__(self):
        self.block = None
        self.difficulty = DIFFICULTY

    # this is here for testing purposes
    def override_difficulty(self, d):
        self.difficulty = d

    def mine(self, block):
        '''
        Finds an appropriate sha256 hash for a block
        '''
        self.block = block
        hash = sha256(str(self.block).encode()).hexdigest()
        while not hash.startswith(self.difficulty * "0"):
            self.block.nonce += 1
            hash = sha256(str(self.block).encode()).hexdigest()
        self.block.hash = hash
        return hash

if __name__ == "__main__":
    miner = Miner()
    b = Block(0, 0, "~some long hex number from a wallet~")

    for i in range(5):
        b.add_transaction("Example transaction, not yet implimentated")

    miner.mine(b)
    print(b)
