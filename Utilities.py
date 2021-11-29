'''
Brad Budden and Josh Bottelberghe
Distributed Systems - Final Project
Utilities.py

Description: This class provides some common
functionality that different types of nodes will
find useful, such as standard methods for sending
and receiving different types of messages.
'''

import socket
import json

class Utilities:

    '''
    Handle the mechanics of sending a message, given a message dict.
    Returns: 1 if successful, 0 otherwise
    '''
    @staticmethod
    def sendMessage(sock: socket.socket, message: dict) -> int:
        msgString = json.dumps(message)
        msgBytes = bytearray(msgString.encode('utf-8'))
        # attempt to send message
        try:
            sock.sendall(msgBytes)
        except:
            # error sending message
            return 0
        return 1

    '''
    Converts message bytes to a python dictionary and returns it
    Returns: None if invalid response, otherwise a dict
    representing the message
    '''
    @staticmethod
    def readMessage(data) -> dict or None:
        try:
            data = str(data, 'utf-8') # convert to string
            return json.loads(data)
        except Exception as e:
            # improperly formatted message
            return None

    