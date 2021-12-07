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
from Constants import Constants

class BlockChainCollection:

    def __init__(self):
        self.main_blockchain = None
        self.blockchain_forks = dict()
    
    def try_add_block(self, block: Block, orphan_blocks: set, pending_transactions: set):
        # TODO: pass
        '''
        Attempts to add a block to any of the existing forks.
        Adds a block to the set of orphan_blocks if it fails.
        Makes a side fork into the main fork if adding the block to
        the side fork makes it longer than the main fork (and 
        manages/updates the set of pending transactions accordingly).
        Returns: 0 if block is an orphan, 1 if block was added to
        main branch or the block was added to a side branch that
        did not become longer than the main branch, and 2 if block was 
        added to a side branch that became the main branch as a result
        '''

        # look at the final hashes of our current blockchain forks, check if
        # the block can be added to the end of any of them
        for final_hash in self.blockchain_forks.keys():
            if block.prev_hash == final_hash:
                # block fits onto the end of a fork, try to add it
                if self.blockchain_forks[final_hash].validate_block(block):
                    self.blockchain_forks[final_hash].add_block(block)
                    # if it's the main fork, remove transactions from pending_transactions
                    # (don't remove pending_transactions when adding to a side fork)
                    if final_hash == self.main_blockchain.block_chain[-1].hash:
                        for txn in block.transactions:
                            pending_transactions.discard(txn.tid)
                    # we've added the block, we can move on
                    continue
        
        # Perhaps the block doesn't fit onto the end of a fork, but rather appends
        # to a block that is now buried in one of the forks. If that block is not
        # too far back, we can make a new fork that ends with that block and then
        # the incoming block. It will be shorter than the main branch, so it may be
        # pruned quickly as other forks grow.
        bc_forks = [item[1] for item in self.blockchain_forks.items()]
        for bc_fork in bc_forks:
            for hash in bc_fork.block_chain[:-Constants.MAX_NEW_BLOCK_INDEX_LAG:-2]:
                if hash == block.hash:
                    # new block adds onto a buried block, create a new BlockChain fork
                    # at that buried block, append the new block, and add this new fork
                    # to self.blockchain_forks
                    new_fork = bc_fork.copy()
                        new_fork.block_chain = new_fork.block_chain[#TODO:]

                    
        


        # prune side branches that are far behind
        for bc_fork in self.blockchain_forks.items():
            if self.main_blockchain.length - bc_fork[1].length >= Constants.SIDE_BLOCKCHAIN_DIFFERENCE_FOR_PRUNING:
                # side branch is too far behind, discard it
                del self.blockchain_forks[bc_fork[0]]


    
    def add_blockchain_fork(self, bc_fork: BlockChain):
        '''
        Adds a BlockChain object to the dictionary of blockchain forks.
        Especially useful when initializing a BlockChainCollection object
        with potentially multiple existing BlockChain forks.
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


