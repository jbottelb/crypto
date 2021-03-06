#!/usr/bin/env python3
'''
Josh Bottelberghe
BlockChain.py

This file contains the Block and BlockChain classes for use
in the blockchain network.
'''
import random
import json
from hashlib import sha256
from .Transaction import Transaction
from collections import defaultdict

class Block:
    def __init__(self, index, prev_hash, pk, nonce=None, transactions=None, hash=None):
        self.index = index
        self.prev_hash = prev_hash
        self.miner_pk = pk
        if nonce:
            self.nonce = nonce
        else:
            self.nonce = random.randint(0, Constants.DIFFICULTY * 100000000)
        if transactions:
            self.transactions = transactions
        else:
            self.transactions = []
        self.hash = None

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def verify_transaction_authenticities(self, send_bad_transaction=False):
        '''
        Checks signatures of all transcations.
        Includes option to return the bad block if one is found.
        DOES NOT CHECK IF THE SENDER CAN SEND THE BALANCE
        (it is quicker to just do that when we validate the block)
        '''
        # return True
        for t in self.transactions:
            if not t.verify_transaction_authenticity():
                if send_bad_transaction:
                    return t
                return False
        return True

    def verify_transactions_are_fundable(self, user_balances: defaultdict):
        '''
        Takes in a BlockChain object's dictionary of user balances and
        determines if all transaction senders have sufficient balances
        for the transaction amounts
        '''
        for t in self.transactions:
            if user_balances[t.sender] < t.amount:
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
        j["Block_Index"]  = self.index
        j["Prev_Hash"]    = self.prev_hash
        j["Miner_PK"]     = self.miner_pk
        j["Nonce"]        = self.nonce
        j["Transactions"] = []
        for t in self.transactions:
            j["Transactions"].append(str(t))
        j["Hash"]         = self.hash
        return j

    def __str__(self):
        block_str = ""
        block_str += "Block index: " + str(self.index) + "\n"
        block_str += "Prev Hash: " + str(self.prev_hash) + "\n"
        block_str += "Nonce: " + str(self.nonce) + "\n"
        block_str += "Coinbase: " + str(Constants.COINBASE) + " -> " + str(self.miner_pk) + "\n"
        block_str += "Transactions\n"
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
        block_str += "Coinbase: " + str(Constants.COINBASE) + " -> " + str(self.miner_pk) + "\n"
        block_str += "Transactions\n"
        for t in self.transactions:
            block_str += str(t) + "\n"

        return block_str

class BlockChain:
    def __init__(self, data:list=None):
        '''
        If creating a blockchain for the first time, don't specify data.
        If using existing blocks, data will be a list of blocks as Block objects.
        '''
        self.block_chain = []
        self.length = 0
        self.accepted_transactions = set()
        self.user_balances = defaultdict(int)
        self.add_block(self.create_genesis(), True)
        if data:
            # read in the data to create the blockchain
            for block in data:
                self.add_block(block)

    def create_genesis(self, data=None) -> dict:
        '''
        Import a genesis text file, if it exists
        Otherwise, create a block where data will be a list of
        genesis transactions (PK, balance)

        Genesis persists as a dictionary, unlike other blocks
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
        # genesis can have any hash (doesn't need to be mined for a specific
        # difficulty)
        block["Hash"] = sha256(json.dumps(block).encode()).hexdigest()
        return block

    def add_block(self, block, genesis=False):
        '''
        Adds a block item to the block chain list.
        Block should be a block object unless genesis is True,
        in which case block should be a dictionary.
        Returns: True on success, False on failure
        '''
        # add transcations
        if genesis:
            self.block_chain.append(block)
            self.length = 1
            return True
        if not genesis:
            for T in block.transactions:
                self.user_balances[T.recipient] += int(T.amount)
                self.user_balances[T.sender] -= int(T.amount)
                self.accepted_transactions.add(T.tid)
            self.user_balances[block.miner_pk] += Constants.COINBASE
        self.block_chain.append(block)
        self.length += 1
        return True

    def validate_transaction(self, T: Transaction):
        '''
        Check if the sender of the transcation can send the amount
        based off thier total in a blockchain
        '''
        if self.user_balances[T["Sender_Public_Key"]] < T["Amount"]:
            return False
        return True

    def validate_block(self, block: Block):
        '''
        Checks if the block is valid and can be added to the chain.
        Checks the block's transcations, hash, index, and previous hash
        '''
        if not block.verify_transaction_authenticities():
            return False
        if not block.verify_transactions_are_fundable(self.user_balances):
            return False
        # verify that none of the new transactions are already in the blockchain
        if block.index == 0:
            # genesis block is a dict
            return True
        else:
            # other blocks are block objects
            for txn in block.transactions:
                if txn.tid in self.accepted_transactions:
                    # we've seen this transaction before, reject block
                    return False
        # index (which started at zero) of a new block should be the
        # same value as the current length of the chain
        if block.index != self.length:
            return False
        hash = sha256(block.string_for_mining().encode()).hexdigest()
        # the hash we get from the block's string representation should
        # match the hash that is included in the block itself
        if hash != block.hash:
            return False
        # the hash must meet the required difficulty
        if not block.hash.startswith(Constants.DIFFICULTY * "0"):
            return False
        # the previous hash must be the hash of the current last block
        # in the blockchain
        if block.index-1 == 0:
            # previous block is genesis block which is a dictionary
            if block.prev_hash != self.block_chain[block.index-1]["Hash"]:
                return False
        # otherwise, the previous block is a normal block object
        elif block.prev_hash != self.block_chain[block.index-1].hash:
            return False
        return True

    def get_pk_total(self, pk):
        '''
        Gets the total balance of a user throught the blockchain
        '''
        return self.user_balances[pk]

    def verify_blockchain(self):
        '''
        Verifies entire blockchain. Genesis block is assumed valid
        except hash.
        '''
        balances = defaultdict(int) # collect running balances for ordering
        prev_hash = None
        for block in self.block_chain:
            if isinstance(block, dict):
                # check hash of the genesis
                to_hash = block.copy()
                del to_hash["Hash"]
                hash = sha256(json.dumps(to_hash).encode()).hexdigest()
                # Make sure we have the right genesis
                if hash != Constants.GENESIS_HASH:
                    return False
                if not hash == block["Hash"]:
                    return False
                for T in block["Transactions"]:
                    balances[T[0]] = int(T[1])
                prev_hash = block["Hash"]
            else:
                # check that block contains the hash of the previous block
                if block.prev_hash != prev_hash:
                    return False
                # check that the hash of the block has the required difficulty
                if not block.hash.startswith(Constants.DIFFICULTY * "0"):
                    return False
                balances[block.miner_pk] += Constants.COINBASE
                for T in block.transactions:
                    if not T.verify_transaction_authenticity():
                        # transaction was not authentic
                        return False
                    if balances[T.sender] < T.amount:
                        # sender did not have large enough balance for the transaction
                        return False
                    # update balances for sender and recipient
                    balances[T.recipient] += T.amount
                    balances[T.sender]    -= T.amount
                hash = sha256(block.string_for_mining().encode()).hexdigest()
                if hash != block.hash:
                    return False
                prev_hash = block.hash
        return True

    def get_last_hash(self):
        '''
        Returns the hash of the most recently added block
        '''
        if self.length == 1:
            return self.block_chain[0]["Hash"]
        return self.block_chain[self.length-1].hash

    def __str__(self):
        '''
        Returns a string of the blockchain
        '''
        string = ""
        for block in self.block_chain:
            string += str(block) + "\n\n"
        return string

    def copy(self):
        copy = BlockChain()
        for block in self.block_chain:
            if isinstance(block, dict):
                continue
            copy.add_block(block)
        return copy

