#!/usr/bin/env python3
'''
Class for a Full Node
'''

from BlockChain import BlockChain, Block

class FullNode:
    def __init__(self, URL):
        self.URL = URL
        self.connections = {}

    def start(self):
        '''
        Runs the main loop, which reads on the sockets and handles the
        messages accordingly.
        '''
        pass

    def handle_message(self):
        pass
