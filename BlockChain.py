#!/usr/bin/env python3

'''
Module for nodes in the system.
Includes functions for keeping track and communicating with other nodes.
'''
import random
import json
from hashlib import sha256
from Transaction import Transaction
from collections import defaultdict

# transactions per block
TPB = 5
# number of leading zeros on computed hashed
DIFFICULTY = 4
# reward for mining Block
COINBASE = 10 # (we do not support depreciation of value for mining blocks)

class BlockChain:
    def __init__(self, data=None):
        '''
        If creating a blockchain for the first time, no data specified
        Otherwise, data will be a json dictionary object that is a list
        of all the blocks
        '''
        self.block_chain = []
        self.length = 0
        self.user_balances = defaultdict(int)
        if data:
            # read in the data to create the blockchain
            for block in data:
                self.add_block(block)
        else:
            # create a blockchain from scratch
            self.block_chain.append(self.create_genesis())

    def create_genesis(self, data=None):
        '''
        Import a genesis text file, if it exists
        Otherwise, do some simple block creation, data will be a list of
        genesis transactions (PK, balance)

        Genisis persists as a dictionary, unlike other blocks
        '''
        block = {}
        block["Block_Index"] = 0
        block["Transactions"] = []
        if data:
            block["Transactions"] = data
        else:
            with open("genesis.json") as f:
                block["Transactions"] = list(json.load(f).items())
        self.length = 1
        for T in block["Transactions"]:
            self.user_balances[T[0]] = int(T[1])
        # genisis can be any diffifulty as it does not need to be mined
        block["Hash"] = sha256(json.dumps(block).encode()).hexdigest()
        return block

    def add_block(self, block):
        '''
        Adds a block item to the block chain list
        '''
        # add transcations
        for T in block.transactions:
            self.user_balances[T.recipient] += int(T.amount)
            self.user_balances[T.sender] -= int(T.amount)
        self.user_balances[block.miner_pk] += COINBASE
        self.block_chain.append(block)
        self.length += 1
        return block

    def validate_transaction(self, T):
        '''
        Check if the sender of the transcation can send the amount
        based off thier total in a blockchain
        '''
        if self.user_balances[T["Sender_Public_Key"]] < T["Amount"]:
            return False
        return True

    def validate_block(self, block):
        '''
        Checks if the block can be validily added to the chain
        '''
        pass

    def get_pk_total(self, pk):
        '''
        Gets the total balance of a user throught the blockchain
        '''
        return self.user_balances[pk]

    def verify_blockchain(self):
        '''
        Verifies entire blockchain

        Genisis block is assumed valid excpet hash
        '''
        balances = defaultdict(int) # collect running balances for ordering
        prev_hash = None
        for block in self.block_chain:
            if block.index == 0:
                # check hash of the genesis
                to_hash = block
                del to_hash["Hash"]
                hash = sha256(json.dumps(to_hash).encode()).hexdigest()
                if not hash == block["Hash"]:
                    return False
                for T in block["Transactions"]:
                    balances[T[0]] = int(T[1])
            else:
                if not block.hash == prev_hash:
                    return False
                if not block.hash.startswith(DIFFICULTY * "0"):
                    return False
                balances[block.miner_pk] += COINBASE
                for T in block.transactions:
                    if not T.verify_transaction():
                        return False
                    if balances[T.sender] < T.amount:
                        return False
                    balances[T.recipient] += T.amount
                    balances[T.sender]    -= T.aomunt
                hash = sha256(block.string_for_mining().encode()).hexdigest()
                if hash != block.hash:
                    return False
            prev_hash = block.hash
        return True

    def __str__(self):
        '''
        Returns a string of the blockchain
        '''
        string = ""
        for block in self.block_chain:
            string += str(block)
        return string

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

    def verify_transactions(self, send_bad_transaction=False):
        '''
        Checks signatures of all transcations
        option to return the bad block if one is found
        DOES NOT CHECK IF THE SENDER CAN SEND THE BALANCE
        (it is quicker to just do that when we validate the block)
        '''
        for t in self.transcations:
            if not t.verify_transaction():
                if send_bad_transaction:
                    return t
                return False
        return True

    def to_string(self):
        '''
        Converts Block to json string
        '''
        # stringify
        return json.dumps(self.to_json())

    def to_json(self):
        '''
        Converts Block to dictionary
        '''
        j = {}
        j["Blcok_Index"]        = self.index
        j["Prev_Hash"]    = self.prev_hash
        j["Miner_PK"]     = self.miner_pk
        j["Nonce"]        = self.nonce
        j["Transactions"] = self.transactions
        j["Hash"]         = self.hash
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


import Wallet
from RSA_Keys import RSA_Keys as RK
if __name__=="__main__":
    '''
    Some cases for testing
    '''
    block_chain = BlockChain()
    block = Block(1, block_chain.block_chain[0]["Hash"], "Josh's PK")
    block.add_transaction(Transaction("Josh's PK", "Brad's PK", "10"))
    block_chain.add_block(block)
    print(block_chain)
    print(block_chain.user_balances)

    John = Wallet(RK.generate_keys())
    print(John.pk)
