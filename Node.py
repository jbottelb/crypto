#!/usr/bin/env python3

'''
Module for nodes in the system.
Includes functions for keeping track and communicating with other nodes.
'''

class Node:
    def __init__(self, port):
        pass

    def message(self, node):
        '''
        message another node using UDP
        '''
        pass

    def broadcast(self, nodes):
        '''
        Send a message to all nodes
        '''
        pass

if __name__=="__main__":
    print("Running Node")
