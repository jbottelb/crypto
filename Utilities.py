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

from MessageTypes import MessageTypes

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
    Checks that the contents of a message are valid depending
    on the message type.
    Returns: True if valid, False otherwise
    '''
    @staticmethod
    def isValidMessage(message: dict) -> bool:
        type = message.get("Type", 0)
        if not type or type not in MessageTypes._value2member_map_:
            return False

        if type == MessageTypes.Get_Seed_Nodes:
            if len(message.keys()) != 1:
                return False
            return True
        elif type == MessageTypes.Get_Neighbors:
            if len(message.keys() != 1):
                return False
            return True
        elif type == MessageTypes.Get_Blockchain:
            # TODO:
            pass
        elif type == MessageTypes.Send_Transaction:
            # TODO:
            pass
        elif type == MessageTypes.Send_Block:
            # TODO:
            pass
        elif type == MessageTypes.Get_Seed_Nodes_Response:
            if len(message.keys()) != 2:
                return False
            seed_nodes = message.get("Nodes", 0)
            if not seed_nodes:
                return False
            if type(seed_nodes) != list:
                return False
            for item in seed_nodes:
                if type(item) != list or len(item) != 2:
                    return False
                if type(item[0]) != str or type(item[1]) != int:
                    return False
            return True
        elif type == MessageTypes.Get_Neighbors_Response:
            if len(message.keys()) != 2:
                return False
            seed_nodes = message.get("Neigbors", 0)
            if not seed_nodes:
                return False
            if type(seed_nodes) != list:
                return False
            for item in seed_nodes:
                if type(item) != list or len(item) != 2:
                    return False
                if type(item[0]) != str or type(item[1]) != int:
                    return False
            return True

        elif type == MessageTypes.Get_Miner_Count:
            # TODO:
            pass

        elif type == MessageTypes.Join_As_Miner:
            # TODO:
            pass

        elif type == MessageTypes.Get_Miner_Count_Response:
            # TODO:
            pass
    
        elif type == MessageTypes.Join_As_Miner_Response:
            # TODO:
            pass


        # TODO: check other types



        return False

    '''
    Converts message bytes to a python dictionary and returns it
    Returns: None if invalid response, otherwise a dict
    representing the message
    '''
    @staticmethod
    def readMessage(data) -> dict or None:
        try:
            data = str(data, 'utf-8') # convert to string
            message = json.loads(data)
            # check that message is a valid message form
            if Utilities.isValidMessage(message):
                return message
        except Exception as e:
            # improperly formatted message
            pass
        return None
        

    