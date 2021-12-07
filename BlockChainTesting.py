#!/usr/bin/env python3
from Wallet import Wallet
from RSA_Keys import RSA_Keys as RK
from Miner import Miner
import random
import json
from hashlib import sha256
from Transaction import Transaction
from collections import defaultdict
from Constants import Constants
from BlockChain import Block, BlockChain


if __name__=="__main__":
    '''
    Testsing the Blockchain class
    '''
    with open("wallets.json") as f:
        wallets = json.load(f)

    Josh = Wallet(wallets["Josh"])
    Brad = Wallet(wallets["Brad"])

    block_chain = BlockChain()
    block = Block(1, block_chain.block_chain[0]["Hash"], wallets["Josh"][0])
    T = Transaction.generate_transaction(Josh, 10, Brad.public_key)
    block.add_transaction(T)

    miner = Miner(wallets["Josh"][0])
    miner.block = block
    miner.mine()
    block = miner.block

    print(block_chain.validate_block(block))

    block_chain.add_block(block)
    print(block_chain)
