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
from types import prepare_class

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
    def _isValidMessage(message: dict) -> bool:
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
            if len(message.keys()) != 6:
                return False
            tid = message.get("Transaction_ID", 0)
            if not tid or type(tid) != str:
                return False
            sender_key = message.get("Sender_Public_Key", 0)
            if not sender_key or type(sender_key) != str:
                return False
            recipient_key = message.get("Recipient_Public_Key", 0)
            if not recipient_key or type(recipient_key) != str:
                return False
            amount = message.get("Amount", 0)
            if not amount or type(amount) != int:
                return False
            signature = message.get("Signature", 0)
            if not signature or type(signature) != str:
                return False
            return True
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
            if len(message.keys()) != 1:
                return False
            return True

        elif type == MessageTypes.Join_As_Miner:
            if len(message.keys()) != 2:
                return False
            searching_for_owner = message.get("Searching_For_Owner", -1)
            if searching_for_owner == -1:
                return False
            if type(searching_for_owner) != str:
                return False
            return True 

        elif type == MessageTypes.Get_Miner_Count_Response:
            if len(message.keys()) != 2:
                return False
            count = message.get("Count", -1)
            if count == -1:
                return False
            if type(count) != int or count < 0:
                return False
            return True
    
        elif type == MessageTypes.Join_As_Miner_Response:
            if len(message.keys()) != 2:
                return False
            full_node_to_try = message.get("Full_Node_To_Try", 0)
            if not full_node_to_try or type(full_node_to_try) != list:
                return False
            if len(full_node_to_try) != 2:
                return False
            if type(full_node_to_try[0]) != str or type(full_node_to_try[1]) != int:
                return False
            return True

        elif type == MessageTypes.Start_New_Block:
            if len(message.keys()) != 4:
                return False
            transactions = message.get("Transactions", 0)
            if not transactions or type(transactions) != list:
                return False
            for item in transactions:
                if type(item) != dict:
                    return False
            previous_hash = message.get("Previous_Hash", 0)
            if not previous_hash or previous_hash != str:
                return False
            block_index = message.get("Block_Index", 0)
            if not block_index or type(block_index) != int or block_index < 0:
                return False
            return True

        elif type == MessageTypes.Start_New_Block_Response:
            if len(message.keys()) != 1:
                return False
            return True


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
            if Utilities._isValidMessage(message):
                return message
        except Exception as e:
            # improperly formatted message
            pass
        return None
        

    