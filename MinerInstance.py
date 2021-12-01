#!/usr/bin/env python3
'''
Implementation of a miner

Miner will mine N amount of times before checking if Node has
new block to work on
'''

import sys
import socket
from BlockChain import Block
from Miner import Miner
from Utilities import readMessage, sendMessage

_, pk, host, port = sys.argv
URL = (host, port)

N = 1000

def listener():
    parent = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    parent.bind(URL)
    parent.listen()
    block = None
    hash = None
    mining = False
    while True:
        # check if there is a message from the Node
        readable, _, _ = select.select([parent], [], [], 60)
        # if so, deal with it
        if readable:
            res = readMessage(parent)
            try:
                block = Block(res["index"], res["prev_hash"], res["pk"])
                for t in red["transactions"]:
                    block.add_transaction(t)
            except Exception as e:
                print(e)
                block = None
        elif hash:
            # send back block
            sendMessage(dict(block), True, None, parent)

        # if mining status should change (enough transactions)
        if block:
            mining = True
        else:
            mining = False

        # if we are mining, mine for a bit
        if Mining and b:
            hash = minier.mine(b, N)

if __name__ == "__main__":
    miner = Miner()


    miner.mine(b)
