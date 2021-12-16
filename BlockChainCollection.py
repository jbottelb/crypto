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
import Constants

class BlockChainCollection:

    def __init__(self):
        self.main_blockchain = None
        self.blockchain_forks = dict()

    def prune_short_forks(self):
        '''
        Prunes side branches that are far behind
        Returns: nothing
        '''
        for bc_fork in self.blockchain_forks.items():
            if self.main_blockchain.length - bc_fork[1].length >= Constants.SIDE_BLOCKCHAIN_DIFFERENCE_FOR_PRUNING:
                # side branch is too far behind, discard it
                del self.blockchain_forks[bc_fork[0]]

    def get_block_by_hash(self, desired_hash: str, orphan_blocks: set) -> Block:
        '''
        Searches for a block with the specified hash
        Returns: Block or None
        '''
        bc_forks = [item[1] for item in self.blockchain_forks.items()] # <- get the BlockChain objects ("forks")
        for bc_fork in bc_forks:
            for block in bc_fork.block_chain[1:]:
                if block.hash == desired_hash:
                    return block
        for block in orphan_blocks:
            if block.hash == desired_hash:
                return block
        return None

    def try_add_block(self, new_block: Block, orphan_blocks: set, pending_transactions: set):
        '''
        Attempts to add a block to any of the existing forks.
        Adds a block to the set of orphan_blocks if it fails.
        Makes a side fork into the main fork if adding the block to
        the side fork makes it longer than the main fork (and
        manages/updates the set of pending transactions accordingly).
        Returns: -1 if block is invalid or already in a fork, 0 if
        block is an orphan, 1 if block was added to main fork,
        2 if the block was added to a side fork that did not become
        longer than the main fork, and 3 if block was added to a
        side fork that became the main fork as a result
        '''

        # check that the transactions in the new block are authentic
        if not new_block.verify_transaction_authenticities():
            return -1

        # look at the final hashes of our current blockchain forks, check if
        # the block can be added to the end of any of them
        found_parent = False
        added_to_main_fork = False
        side_fork_became_main_fork = False
        for final_hash in self.blockchain_forks.keys():
            if new_block.prev_hash == final_hash:
                # block fits onto the end of a fork, try to add it
                if self.blockchain_forks[final_hash].validate_block(new_block):
                    self.blockchain_forks[final_hash].add_block(new_block)
                    # update the entry in the dictionary with the new final hash value as its key
                    self.blockchain_forks[new_block.hash] = self.blockchain_forks[final_hash].copy()
                    del self.blockchain_forks[final_hash]
                    # mark that we added the block to the end of a fork
                    found_parent = True
                    # if we added to the main fork, remove transactions from pending_transactions
                    # (don't remove pending_transactions when adding to a side fork)
                    if final_hash == self.main_blockchain.block_chain[-1].hash:
                        # update the individual copy of the main blockchain fork as well
                        self.main_blockchain = self.blockchain_forks[new_block.hash].copy()
                        added_to_main_fork = True
                        transactions_to_discard = []
                        for txn in new_block.transactions:
                            for t in pending_transactions:
                                if txn.tid == t.tid:
                                    transactions_to_discard.append(t)
                        for txn in transactions_to_discard:
                            pending_transactions.discard(txn)
                        # we've added the block, we can move on
                        break
                    # if it's not the main fork, we must check if the side fork has
                    # grown longer than the main fork
                    elif self.blockchain_forks[new_block.hash].length > self.main_blockchain.length:
                        side_fork_became_main_fork = True
                        # find the last common ancestor block
                        common_ancestor_index = -1
                        for index, old_side_fork_block in enumerate(self.blockchain_forks[new_block.hash].block_chain):
                            # handle genesis block scenario (because it's a dict)
                            if index == 0:
                                if old_side_fork_block["Hash"] == self.main_blockchain.block_chain[index]["Hash"]:
                                    common_ancestor_index = index
                                    continue
                                else:
                                    # no blocks are shared between the two forks
                                    break
                            # now handle block indices > 0
                            if old_side_fork_block.hash == self.main_blockchain.block_chain[index].hash:
                                common_ancestor_index = index
                        # Now we have the index of the last block that the two forks share.
                        # We must take all transactions (except COINBASE txns) from the divergent
                        # blocks of the old main branch and add them back to pending_transactions
                        if common_ancestor_index == -1:
                            # no shared blocks, handle transactions from genesis block (a dict)
                            for txn in self.main_blockchain.block_chain[0]["Transactions"]:
                                pending_transactions.add(txn.copy())
                            # also, remove transactions from pending transactions if they are
                            # in the new main fork's genesis block
                            transactions_to_discard = []
                            for txn in self.blockchain_forks[new_block.hash].block_chain[0]["Transactions"]:
                                for t in pending_transactions:
                                    if txn["Transaction_ID"] == t.tid:
                                        transactions_to_discard.append(t)
                            for txn in transactions_to_discard:
                                pending_transactions.discard(txn)
                            common_ancestor_index = 0
                        # now handle blocks from after common_ancestor and onwards
                        for divergent_block in self.main_blockchain.block_chain[common_ancestor_index+1:]:
                            for txn in divergent_block.transactions:
                                pending_transactions.add(txn.copy())
                        # Then we must remove all transactions in the new main branch (from common
                        # ancestor onward) from pending_transactions
                        transactions_to_discard = []
                        for divergent_block in self.blockchain_forks[new_block.hash].block_chain[common_ancestor_index+1:]:
                            for txn in divergent_block.transactions:
                                for t in pending_transactions:
                                    if txn.tid == t.tid:
                                        transactions_to_discard.append(t)
                        for txn in transactions_to_discard:
                            pending_transactions.discard(txn)
                        # update the individual copy of the main blockchain fork
                        self.main_blockchain = self.blockchain_forks[new_block.hash].copy()
                else:
                    # block fits onto the end of a fork, but it's not valid
                    return -1

        # Perhaps the block doesn't fit onto the end of a fork, but rather appends
        # to a block that is now buried in one of the forks. If that block is not
        # too far back, we can make a new fork that ends with that block followed by
        # the incoming block. It will be shorter than (or equal to) the main branch,
        # so it may be pruned quickly as other forks grow.
        if not found_parent:
            found_buried_parent = False
            bc_forks = [item[1] for item in self.blockchain_forks.items()] # <- get the BlockChain objects ("forks")
            for bc_fork in bc_forks:
                if found_buried_parent:
                    # now we can move on
                    break
                # consider all buried blocks in the fork
                for index, buried_block in enumerate(bc_fork.block_chain[:-1]):
                    # check if a new block adds onto a buried block, and also check that the next block in
                    # the fork isn't the same as the new block we are trying to add (could occur if we get
                    # the same block two or more times)
                    if new_block.prev_hash == buried_block.hash and bc_fork.block_chain[index+1].hash != new_block.hash:
                        # new block adds onto a buried block, create a new BlockChain fork
                        # at that buried block, append the new block, and add this new fork
                        # to self.blockchain_forks
                        new_fork = bc_fork.copy()
                        new_fork.block_chain = new_fork.block_chain[:buried_block.index + 1]
                        if new_fork.validate_block(new_block):
                            # just add the block, don't touch the pending_transactions set
                            new_fork.add_block(new_block.copy())
                            # add the new fork to our collection of forks
                            self.add_blockchain_fork(new_fork)
                            found_buried_parent = True
                            break

        if not found_parent and not found_buried_parent:
            # orphan block
            orphan_blocks.add(new_block.copy())
            return 0
        if found_parent and added_to_main_fork:
            # added to main fork
            return 1
        if found_parent and side_fork_became_main_fork:
            # added to side fork that became main fork
            return 3
        if found_parent or found_buried_parent:
            # added to side fork that did not become main fork
            return 2
        return -1

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
            self.main_blockchain = bc_fork.copy()
            # add the fork to our dictionary of forks, with a key that stores
            # the hash of its last block
            self.blockchain_forks[bc_fork.get_last_hash()] = bc_fork.copy()
            return 2
        elif len(bc_fork.block_chain) > self.main_blockchain.length:
            # new fork is longer than current main fork, so make it our main fork
            self.main_blockchain = bc_fork.copy()
            # add fork to our dict of forks
            self.blockchain_forks[bc_fork.get_last_hash()] = bc_fork.copy()
            return 2
        else:
            # just add the fork to our dict of forks
            self.blockchain_forks[bc_fork.get_last_hash()] = bc_fork.copy()
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
            if bc_last_hash != self.main_blockchain.get_last_hash():
                print(self.blockchain_forks[bc_last_hash])
        print("---- End Side BlockChain Forks ----")
        print("\n")
