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
    John = Wallet(wallets["John"])
    Mary = Wallet(wallets["Mary"])

    block_chain = BlockChain()
    block = Block(1, block_chain.get_last_hash(), wallets["Josh"][0])
    T = Transaction.generate_transaction(Josh, 100, Brad.public_key)
    block.add_transaction(T)

    miner = Miner(wallets["Josh"][0])
    miner.block = block
    miner.mine()
    block = miner.block

    if block_chain.validate_block(block):
        block_chain.add_block(block)

    block = Block(2, block_chain.get_last_hash(), wallets["Josh"][0])
    for i in range(10):
        T = Transaction.generate_transaction(John, i, Mary.public_key)
        block.add_transaction(T)

    miner.block = block
    miner.mine()
    block = miner.block

    if block_chain.validate_block(block):
        block_chain.add_block(block)

    if block_chain.verify_blockchain():
        print("Josh", block_chain.get_pk_total(Josh.public_key))
        print("Brad", block_chain.get_pk_total(Brad.public_key))
        print("Mary", block_chain.get_pk_total(Mary.public_key))
        print("John", block_chain.get_pk_total(John.public_key))
