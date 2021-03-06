#!/usr/bin/env python3
'''
A simple CLI Lightweight Client
'''

from BlockChain import BlockChain, Block
from Transaction import Transaction
from RSA_Keys import RSA_Keys as RK
from Wallet import Wallet
import json, sys
from Messaging import Messaging,  MessageTypes
import socket
from Crypto.Math._IntegerGMP import IntegerGMP

def prompt():
    print("                                         \n\
Choose one of these options:                        \n\
    g (filename) generate wallet file              \n\
    l (filename) load wallet file                   \n\
    t (amount) send a transaction, then (user name)   \n\
    b check balance of the loaded wallet           \n\
    u update blockchain                            \n\
    q quit                                         \n\
    ")
    return input("----> ")

def load_wallet(filename):
    with open(filename) as f:
        data = json.load(f)
        print("\nWallet loaded from file", filename)
        return Wallet([data["pk"], data["sk"]])

def generate_wallet(filename):
    d = {}
    pk, sk = RK.generate_keys()
    d["pk"], d["sk"]  = str(pk.decode()), str(sk.decode())
    with open(filename, "w") as f:
        json.dump(d, f)
    print("New keys stored in file", filename)

def decorate_recipient_public_key(recipient):
    beginning = "-----BEGIN PUBLIC KEY-----"
    ending = "-----END PUBLIC KEY-----"
    print(beginning + recipient + ending)
    return beginning + recipient + ending


def create_and_send_transaction(wallet, recipient, amount, trusted_node):
    if not wallet:
        print("You need to load a wallet before sending a transaction")
        return
    # re-decorate the recipient's public key
    # recipient = decorate_recipient_public_key(recipient)
    T = Transaction(wallet.public_key, recipient, amount)
    T.sign(wallet.secret_key)
    try:
        send_transaction(T, trusted_node)
    except:
        pass

def send_transaction(T: Transaction, trusted_node):
    '''
    Sends a transaction to a full node
    '''
    print("Got to send_transaction")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    message = T.to_json(sig=True)
    message["Type"] = MessageTypes.Send_Transaction
    message["Previous_Message_Recipients"] = []
    # message["Transaction_ID"] = str(T.tid)
    # message["Sender_Public_Key"] = str(T.sender)
    # message["Recipient_Public_Key"] = str(T.recipient)
    # message["Amount"] = T.amount
    # message["Signature"] = list(T.signature) # send bytes as array of ints
    sock.connect(trusted_node)
    sock.settimeout(5)
    r = Messaging.sendMessage(message, True, sock=sock, connections={})
    if r:
        print("Transaction sent to Node")
    else:
        print("Issue sending block to trusted node")
        return
    try:
        response = Messaging.readMessage(sock)
        if response is None:
            print("Unable to determine if transaction was deemed valid by trusted node")
            return
        if response["Valid"] == "Yes":
            print("Transaction valid according to trusted node")
        else:
            print("Transaction currently invalid according to trusted node")
    except:
        return


def get_blockchain(trusted_node) -> BlockChain:
    try:
        bc = Messaging.getBlockchain(trusted_node)
        if bc is not None:
            print("Updated local Blockchain copy")
            return bc
        else:
            print("Blockchain update could not be performed")
            return None
    except:
        print("Blockchain update could not be performed")
        return None
        

def get_wallet_balance(wallet: Wallet, blockchain_copy: BlockChain):
    return blockchain_copy.user_balances[wallet.public_key]

def read_default_users():
    with open("DefaultUsers.json") as f:
        data = json.load(f)
        print(f"\nDefault Users: {[key for key in data.keys()]}")
    return data

def main():

    if len(sys.argv) != 1 and len(sys.argv) != 3:
        print("Usage: python3 LightWeightCLI.py <trusted host> <port of trusted host>")
        exit(-1)
    trusted_node_provided = False
    trusted_node = None
    if len(sys.argv) == 3:
        try:
            trusted_node = (sys.argv[1], int(sys.argv[2]))
            trusted_node_provided = True
        except:
            print("Usage: python3 LightWeightCLI.py <trusted host> <port on trusted host>")
            exit(-1)
    if trusted_node_provided:
        if not Messaging.pingNode(trusted_node):
            print("Trusted node not running")
            exit(-1)
        print("Trusted node is active")
    else:
        print("Give port and hostname of fullnode")

    if trusted_node is None:
        print("Failed to find active full node")
        exit(-1)

    # start with the genesis block created
    blockchain_copy = BlockChain()

    users_dict = read_default_users()

    wallet = None
    choice = prompt()
    print()
    while choice != "q":
        try:
            choice = choice.split(" ")
            if choice[0] == "g":
                generate_wallet(choice[1])
            elif choice[0] == "l":
                wallet = load_wallet(choice[1])
            elif choice[0] == "t":
                if wallet is None:
                    print("Load a valid wallet first")
                else:
                    amount = choice[1]
                    res = input("(user name) or z to break ---->  ")
                    if res != 'z':
                        create_and_send_transaction(wallet, users_dict.get(res, ""), amount, trusted_node)
                    else:
                        continue
            elif choice[0] == "b":
                if wallet is None:
                    print("Load a valid wallet first")
                else:
                    try:
                        print()
                        print(get_wallet_balance(wallet, blockchain_copy))
                    except:
                        print("Cannot get balance for wallet's public key")
            elif choice[0] == "u":
                bc_copy = get_blockchain(trusted_node)
                if bc_copy is not None:
                    blockchain_copy = bc_copy
            choice = prompt()
        except:
            choice = prompt()

if __name__=="__main__":
    main()
