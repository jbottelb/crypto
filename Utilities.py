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
import http.client
from MessageTypes import MessageTypes
from Constants import Constants

class Utilities:

    '''
    Checks that the contents of a message are valid depending
    on the message type.
    Returns: True if valid, False otherwise
    '''
    @staticmethod
    def _isValidMessage(message: dict) -> bool:
        msgtype = message.get("Type", 0)
        if not msgtype or msgtype not in [MessageTypes.__dict__[key] for key in MessageTypes.__dict__.keys() if not key.startswith("__")]:
            return False

        if msgtype == MessageTypes.Get_Seed_Nodes:
            if len(message.keys()) != 1:
                return False
            return True
        elif msgtype == MessageTypes.Get_Neighbors:
            if len(message.keys() != 1):
                return False
            return True
        elif msgtype == MessageTypes.Get_Blockchain:
            if len(message.keys() != 1):
                return False
            return True
        elif msgtype == MessageTypes.Send_Transaction:
            if len(message.keys()) != 7:
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
            prev_recipients = message.get("Previous_Message_Recipients", -1)
            if prev_recipients == -1 or type(prev_recipients) != list:
                return False
            for item in prev_recipients:
                if len(item) != 2:
                    return False
            return True
        elif msgtype == MessageTypes.Send_Block:
            if len(message.keys()) != 7:
                return False
            block_index = message.get("Block_Index", -1)
            if block_index == -1 or type(block_index) != int:
                return False
            prev_hash = message.get("Prev_Hash", 0)
            if not prev_hash or type(prev_hash) != str:
                return False
            nonce = message.get("Nonce", None)
            if nonce is None or type(nonce) != int:
                return False
            hash = message.get("Hash", 0)
            if not hash or type(hash) != str:
                return False
            transactions = message.get("Transactions", None)
            if transactions is None or type(transactions) != list:
                return False
            for item in transactions:
                if type(item) != dict:
                    return False
            prev_recipients = message.get("Previous_Message_Recipients", -1)
            if prev_recipients == -1 or type(prev_recipients) != list:
                return False
            for item in prev_recipients:
                if len(item) != 2:
                    return False
            return True

        elif msgtype == MessageTypes.Get_Seed_Nodes_Response:
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
        elif msgtype == MessageTypes.Get_Neighbors_Response:
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

        elif msgtype == MessageTypes.Get_Miner_Count:
            if len(message.keys()) != 1:
                return False
            return True

        elif msgtype == MessageTypes.Join_As_Miner:
            if len(message.keys()) != 2:
                return False
            searching_for_owner = message.get("Searching_For_Owner", -1)
            if searching_for_owner == -1:
                return False
            if type(searching_for_owner) != str:
                return False
            return True 

        elif msgtype == MessageTypes.Get_Miner_Count_Response:
            if len(message.keys()) != 2:
                return False
            count = message.get("Count", -1)
            if count == -1:
                return False
            if type(count) != int or count < 0:
                return False
            return True
    
        elif msgtype == MessageTypes.Join_As_Miner_Response:
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

        elif msgtype == MessageTypes.Start_New_Block:
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

        elif msgtype == MessageTypes.Start_New_Block_Response:
            if len(message.keys()) != 1:
                return False
            return True
        
        elif msgtype == MessageTypes.Get_Blockchain_Response:
            if len(message.keys()) != 7:
                return False
            block_index = message.get("Block_Index", -1)
            if block_index == -1 or type(block_index) != int:
                return False
            prev_hash = message.get("Prev_Hash", 0)
            if not prev_hash or type(prev_hash) != str:
                return False
            num_blocks_left = message.get("Num_Blocks_Left_To_Come", -1)
            if num_blocks_left == -1 or type(num_blocks_left) != int:
                return False
            nonce = message.get("Nonce", None)
            if nonce is None or type(nonce) != int:
                return False
            hash = message.get("Hash", 0)
            if not hash or type(hash) != str:
                return False
            transactions = message.get("Transactions", None)
            if transactions is None or type(transactions) != list:
                return False
            for item in transactions:
                if type(item) != dict:
                    return False
            return True

        # TODO: check other types if more are added
        return False

    '''
    Attempts to read from the provided socket. Handles socket issues
    and invalid message formats. Will close sockets with issues and
    remove them from the provided connections dictionary. Converts 
    message bytes to a python dictionary and returns it, otherwise indicates
    an error. 
    Returns: None if invalid message or socket issue, otherwise a dict
    representing the message
    '''
    @staticmethod
    def readMessage(sock: socket.socket, connections: dict = None) -> dict or None:
        try:
            data = sock.recv(Constants.BUF_SIZE)
        except ConnectionResetError:
            # don't exit if client ends connection,
            # just remove the connection from the dict
            sock.close()
            if connections is not None:
                del connections[sock]
            return None
        except socket.timeout:
            # in cases where a socket has a timeout set, return None
            # when we hit that timeout
            return None
        if not data:
            # client may have ended the connection
            sock.close()
            if connections is not None:
                del connections[sock]
            return None
        if connections is not None:
            print(f"Handling message from {connections[sock]}...")
        try:
            data = str(data, 'utf-8') # convert to string
            message = json.loads(data)
            # check that message is a valid message form
            print(f"Message to be validated: {message}")
            if Utilities._isValidMessage(message):
                print("message is valid")
                return message
        except:
            # improperly formatted message
            print("message is not valid")
            pass
        return None

    '''
    Tries to connect to the server by looking up the service with 
    the specified project_name in catalog.cse.nd.edu.
    Returns: boolean representing whether a connection was made
    '''
    @staticmethod
    def _connectToNameServer(sock: socket.socket) -> bool:
        try:
            catalog_conn = http.client.HTTPConnection(Constants.CATALOG_ENDPOINT, Constants.CATALOG_PORT)
            catalog_conn.request("GET", "/query.json")
            result = catalog_conn.getresponse()
            data = result.read()
            data = data.decode('utf-8')
            services = json.loads(data)
            catalog_conn.close()
        except:
            # issue making connection to catalog server
            return False

        connection_made = False
        for service in services:
            if service.get('type', '') == 'nameserver':
                if service.get('project', '') == Constants.PROJECT_NAME:
                    host = service.get('name', '')
                    port = service.get('port', '')
                    try:
                        # attempt connection to name server
                        sock.connect((host, port))
                        connection_made = True
                    except:
                        # Connection Error, try another service
                        # (perhaps we restarted our server on another port)
                        continue
                    return connection_made
        return connection_made
    
    '''
    Sends a request to the name server to get a list of active seed nodes.
    Returns: active seed nodes if successful, None otherwise
    '''
    @staticmethod
    def getActiveSeedNodes() -> list or None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if not Utilities._connectToNameServer(sock):
                # Name server is down, Full Node must wait/retry or provide a trusted node to get started
                sock.close()
                return None
        except ConnectionRefusedError:
            # Name server is down, Full Node must wait/retry or provide a trusted node to get started
            sock.close()
            return None
        # send request for seed nodes to the name server
        if not Utilities.sendMessage(sock, {"Type": MessageTypes.Get_Seed_Nodes}):
            # issue sending seed nodes request to name server
            sock.close()
            return None
        # wait for response from name server (until timeout)
        sock.settimeout(5)
        response = Utilities.readMessage(sock)
        if response is not None:
            if response.get("Type", 0) == MessageTypes.Get_Seed_Nodes_Response:
                sock.close()
                return response.get("Nodes", None)
        sock.close()
        return None

    '''
    Attempts to get the neighbors of a provided full node. If that node 
    is not not alive or communication issues occur, it indicates this 
    with a None response.
    Returns: list of neighbors (can be empty) if successful, None otherwise
    '''
    @staticmethod
    def getNeighbors(addr: tuple) -> list or None:
        returnList = None
        message = {"Type": MessageTypes.Get_Neighbors}
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(addr)
        except:
            # issue connecting to desired full node
            return None
        rc = Utilities.sendMessage(sock, message)
        if rc:
            # sent message successfully to trusted node,
            # read response
            response = Utilities.readMessage(sock)
            if response is not None:
                returnList = response.get("Neighbors", None)
        sock.close()
        return returnList
    
    '''
    Handles the mechanics of sending a message, given a message dict. If a node wants the
    socket to be kept open, it must provide a connections dict for the socket to be added to.
    Returns: 1 if successful, 0 otherwise
    '''
    @staticmethod
    def sendMessage(addr: tuple, message: dict, keepSocketOpen: bool, connections: dict = None) -> int:
        if keepSocketOpen and not connections:
            # must provide a connections dict if socket is to be kept open for future use
            return 0
        msgString = json.dumps(message)
        msgBytes = bytearray(msgString.encode('utf-8'))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # try to connect, save socket if required
            sock.connect(addr)
            if keepSocketOpen:
                connections[sock] = f"{addr[0]}:{addr[1]}"
        except:
            # issue connecting to address or saving socket
            return 0
        # attempt to send message
        try:
            sock.sendall(msgBytes)
        except:
            # error sending message
            return 0
        if not keepSocketOpen:
            sock.close()
        return 1
    
    '''
    Attempts to send a response message on an open socket.
    Closes socket afterwards.
    Returns: nothing
    '''
    def sendResponse(sock: socket.socket, response: dict):
        responseString = json.dumps(response)
        responseBytes = bytearray(responseString.encode('utf-8'))
        # attempt to send message
        try:
            sock.sendall(responseBytes)
        except:
            # error sending message
            pass
        sock.close()

    '''
    sendResponse - take in a socket, send message, close socket
    sendMessage - keepSocketOpen? - Yes - take in addr, take in connections, create socket, add to connections, send message
                                    - No  - take in addr, create socket, send message, close socket (sending messages for which you need no response)

    When to keep a socket open? When you expect to get a response from that socket after a message you are sending.
    '''

    