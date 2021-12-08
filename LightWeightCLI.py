#!/usr/bin/env python3
'''
A simple CLI Lightweight Client
'''

from BlockChain import BlockChain, Block
from Transaction import Transaction
from RSA_Keys import RSA_Keys as RK
from Wallet import Wallet
import json, sys
from Utilities import Utilities
from MessageTypes import MessageTypes
import socket

BLOCKCHAIN_COPY = None
try:
    URL = (sys.argv[1], int(sys.argv[2]))
except Exception as e:
    print(e)
    exit(1)

def prompt():
    print("                                         \n\
Choose one of these options:                        \n\
    g (filename) generate wallet file              \n\
    l (filename) load that wallet file             \n\
    t (recipient pk) (amount) send a transaction   \n\
    b check balance of the loaded wallet           \n\
    u update blockchain                            \n\
    q quit                                         \n\
    ")
    return input("----> ")

def load_wallet(filename):
    with open(filename) as f:
        data = json.load(f)
        print("Wallet loaded from file", filename)
        return Wallet([data["pk"], data["sk"]])

def generate_wallet(filename):
    d = {}
    pk, sk = RK.generate_keys()
    d["pk"], d["sk"]  = str(pk.decode()), str(sk.decode())
    with open(filename, "w") as f:
        json.dump(d, f)
    print("New keys stored in file", filename)

def create_and_send_transaction(wallet, recipient, amount):
    if not wallet:
        print("Load a wallet!")
        return
    T = Transaction(wallet.public_key, recipient, amount)
    T.sign(wallet.secret_key)
    send_transaction(T)
    print("Transaction sent to Node")

def send_transaction(T):
    '''
    Sends a transaction to a full node
    '''
    message = {"Type": MessageTypes.Send_Transaction}

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    message["Transaction_ID"] = str(T.tid)
    message["Sender_Public_Key"] = str(T.sender)
    message["Recipient_Public_Key"] = str(T.recipient)
    message["Amount"] = T.amount
    print(T.signature)
    print(str(T.signature))
    message["Signature"] = str(T.signature)
    message["Previous_Message_Recipients"] = []
    sock.connect(URL)
    sock.settimeout(5)
    r = Utilities.sendMessage(message, True, sock=sock)
    print(r)

def get_blockchain():
    print(Utilities.getBlockchain(URL))

def main():
    wallet = None
    choice = prompt()
    print()
    while choice != "q":
        #try:
        choice = choice.split(" ")
        if choice[0] == "g":
            generate_wallet(choice[1])
        elif choice[0] == "l":
            wallet = load_wallet(choice[1])
        elif choice[0] == "t":
            create_and_send_transaction(wallet, choice[1], choice[2])
        elif choice[0] == "b":
            pass
        elif choice[0] == "u":
            BLOCKCHAIN_COPY = get_blockchain()
        else:
            print("Invalid choice")
        #except Exception as e:
        #    print(e)
        choice = prompt()

if __name__=="__main__":
    main()
