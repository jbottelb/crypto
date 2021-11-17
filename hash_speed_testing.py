#!/usr/bin/env python3
'''
Used for finding how long different difficulties take
'''

from MinerMk1 import Miner
from BlockChain import DIFFICULTY, Block
import time
import random

trials = 100

def main():
    m = Miner()
    blocks = []
    for i in range(trials):
        b = Block(0, 0, "Public key of some sort")
        for i in range(5):
            b.add_transaction(str(random.randbytes(32)))
        blocks.append(b)
    # Measure each difficulty
    for i in range(1, 8):
        m.override_difficulty(i)
        print("Degree of Difficulty:", i)
        start = time.time()
        for b in blocks:
            m.mine(b)
        total = time.time() - start
        print("Time for", trials, "blocks: ", str(total))
        print("Average time per hash: ", str(total/trials))



if __name__ == "__main__":
    main()
