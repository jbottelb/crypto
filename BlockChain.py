#!/usr/bin/env python3

'''
Module for nodes in the system.
Includes functions for keeping track and communicating with other nodes.
'''
import random
import json
from Transaction import Transaction

# transactions per block
TPB = 5
# number of leading zeros on computed hashed
DIFFICULTY = 4
# reward for mining Block
COINBASE = 10 # (we do not support depreciation of value for mining blocks)

class BlockChain:
    def __init__(self):
        self.block_chain = []
        self.block_chain.append(create_genesis())
        self.length = 1

    def create_genesis():
        return None

class Block:
    def __init__(self, index, prev_hash, pk):
        self.index = index
        self.prev_hash = prev_hash
        self.miner_pk = pk
        self.nonce = random.randint(0, DIFFICULTY * 100000000)

        self.transactions = []
        self.hash = None

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def verify_transactions(self, send_bad_block=False):
        '''
        Checks signatures of all transcations
        option to return the bad block if one is found
        '''
        for t in self.transcations:
            if not Transaction.verify_transaction(t):
                if send_bad_block:
                    return t
                return False
        return True

    def to_json(self):
        '''
        Converts Block to json string
        '''
        j = {}
        j["index"]        = self.index
        j["prev_hash"]    = self.prev_hash
        j["miner_pk"]     = self.miner_pk
        j["nonce"]        = self.nonce
        j["transactions"] = self.transactions
        j["hash"]         = self.hash
        # stringify
        return json.dumps(j)

    def __dict__(self):
        '''
        Converts Block to json string
        '''
        j = {}
        j["index"]        = self.index
        j["prev_hash"]    = self.prev_hash
        j["miner_pk"]     = self.miner_pk
        j["nonce"]        = self.nonce
        j["transactions"] = self.transactions
        j["hash"]         = self.hash
        # stringify
        return j

    def __str__(self):
        block_str = ""
        block_str += "Block index: " + str(self.index) + "\n"
        block_str += "Prev Hash: " + str(self.prev_hash) + "\n"
        block_str += "Nonce: " + str(self.nonce) + "\n"
        block_str += "Coinbase: " + str(COINBASE) + " -> " + str(self.miner_pk) + "\n"
        block_str += "Transactions"
        for t in self.transactions:
            block_str += str(t) + "\n"
        if self.hash:
            block_str += "Hash: " + self.hash
        return block_str

    def string_for_mining(self):
        block_str = ""
        block_str += "Block index: " + str(self.index) + "\n"
        block_str += "Prev Hash: " + str(self.prev_hash) + "\n"
        block_str += "Nonce: " + str(self.nonce) + "\n"
        block_str += "Coinbase: " + str(COINBASE) + " -> " + str(self.miner_pk) + "\n"
        block_str += "Transactions"
        for t in self.transactions:
            block_str += str(t) + "\n"

        return block_str
