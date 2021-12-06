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
        if data:
            # read in the data to create the blockchain
            for block in data:
                self.add_block(block)
        else:
            # create a blockchain from scratch
            self.block_chain.append(create_genesis())
        # holds the balances of all users
        self.user_balances = defaultdict(int)

    def create_genesis(self, data=None):
        '''
        Import a genesis text file, if it exists
        Otherwise, do some simple block creation, data will be a list of
        genesis transactions (PK, balance)
        '''
        block = {}
        block["Block_Index"] = 0
        block["transactions"] = []
        if data:
            block["transactions"] = data
        else:
            with open("genesis.json") as j:
                block["transactions"] = list(json.load(f).items())
        self.length = 1
        for T in block["transactions"]:
            self.user_balances[T[0]] = int(T[1])
        # genisis can be any diffifulty as it does not need to be mined
        block["hash"] = sha256(json.dumps(block).encode()).hexdigest()
        return self.block_chain[0]

    def add_block(self, data):
        '''
        Adds a dictionary of a block to the blockchain list
        '''
        if data["index"] == 0:
            self.block_chain.append(create_genesis(data))
            return self.block_chain[0]
        block = Block(data["Block_Index"], data["Prev_Hash"], data["Miner_PK"])
        # add transcations
        for T in data["transactions"]:
            self.user_balances[T["Recipient_Public_Key"]] += T["Amount"]
            self.user_balances[T["Sender_Public_Key"]] -= T["Amount"]
            block.add_transaction(T)
        block["Hash"]       = data["Hash"]
        block["Nonce"]      = data["Nonce"]
        self.user_balances["miner_pk"] += COINBASE
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
            if block["Block_Index"] == 0:
                # check hash of the genesis

                for T in block["transactions"]:
                    balances[T[0]] = int(T[1])
            else:
                for T in block["Transactions"]:
                    if not verify_transaction(T):
                        return False
                    balances[T["Recipient_Public_Key"]] += T["Amount"]
                    balances[T["Sender_Public_Key"]] -= T["Amount"]

            prev_hash = block["Hash"]
        return True


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
            if not Transaction.verify_transaction(t):
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
