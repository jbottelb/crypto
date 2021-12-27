'''
Implimentation of a Full Node
Josh Bottelberghe
'''
from context import Blockchain
from Blockchain import Constants, BlockChain, Block, Transaction, Messaging, MessageTypes

class FullNode:
    def __init__(self, addr):
        self.addr = addr
        self.miners = set()
        self.connections = set()

        self.blockchain = BlockChain()

    def run(self):
        pass





if __name__=="__main__":
    pass