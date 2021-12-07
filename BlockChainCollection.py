'''
Brad Budden and Josh Bottelberghe
Distributed Systems - Final Project
BlockChainCollection.py

Description: This class will implement
the management of multiple forks of
blockchains. It will identify the main
fork and handle insertions of new blocks
into an appropriate fork based on the
prev_hash of the block and the block's
validity in that fork (i.e., whether
transactions are valid based on the 
state of that fork)
'''

from BlockChain import Block, BlockChain
from Transaction import Transaction

class BlockChainCollection:

    def __init__(self):
        self.main_blockchain = None
        self.blockchain_forks = dict()
    
    def try_add_block(self, block: Block, orphan_blocks: set, pending_transactions: set):
        # TODO: pass
        '''
        Attempts to add a block to any of the existing forks.
        Adds a block to the set of orphan_blocks if it fails.
        Makes a side fork the main fork if adding the block to
        the side fork makes it longer than the main fork (and 
        manages/updates the set of pending transactions accordingly).
        Returns: 0 if block is an orphan, 1 if block was added to
        main branch or the block was added to a side branch that
        did not become longer than the main branch, and 2 if block was 
        added to a side branch that became the main branch as a result
        '''
    
    def add_blockchain_fork(self, bc_fork: BlockChain):
        '''
        Adds a BlockChain object to the dictionary of blockchain forks.
        Especially useful when initializing a BlockChainCollection object
        with an existing BlockChain object.
        Returns: 1 if the bc_fork did not become the main fork, 2 if
        bc_fork became the main fork
        '''
        if not self.main_blockchain:
            # if no main fork, make the fork our main fork
            self.main_blockchain = bc_fork
            # add the fork to our dictionary of forks, with a key that stores
            # the hash of its last block
            self.blockchain_forks[bc_fork.block_chain[-1].hash] = bc_fork
            return 2
        elif len(bc_fork.block_chain) > self.main_blockchain.length:
            # new fork is longer than current main fork, so make it our main fork
            self.main_blockchain = bc_fork
            # add fork to our dict of forks
            self.blockchain_forks[bc_fork.block_chain[-1].hash] = bc_fork
            return 2
        else:
            # just add the fork to our dict of forks
            self.blockchain_forks[bc_fork.block_chain[-1].hash] = bc_fork
            return 1
    
    def print_main_fork(self):
        print(self.main_blockchain)

    def print_forks(self):
        print("---- Start Main BlockChain Fork ----")
        print(self.main_blockchain)
        print("---- End Main BlockChain Fork ----")
        print("\n")
        print("---- Start Side BlockChain Forks ----")
        for bc_last_hash in self.blockchain_forks.keys():
            # don't print the main blockchain again
            if bc_last_hash != self.main_blockchain.block_chain[-1].hash:
                print(self.blockchain_forks[bc_last_hash])
        print("---- End Side BlockChain Forks ----")


