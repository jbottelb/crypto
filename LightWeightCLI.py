#!/usr/bin/env python3
'''
A simple CLI Lightweight Client
'''

from BlockChain import BlockChain, Block
from Transaction import Transaction
from RSA_Keys import RSA_Keys as RK
from Wallet import Wallet
import json

WALLET          = None
BLOCKCHAIN_COPY = None

def prompt():
    print("                                         \n\
Choose one of these options:                        \n\
    -g (filename) generate wallet file              \n\
    -l (filename) load that wallet file             \n\
    -t (recipient pk) (amount) send a transaction   \n\
    -b check balance of the loaded wallet           \n\
    -u update blockchain                            \n\
    -q quit                                         \n\
    ")
    return input("----> ")

def load_wallet(filename):
    with open(filename) as f:
        data = json.load(f)
        WALLET = Wallet([data["pk"], data["sk"]])
    print("Wallet loaded from file", filename)


def generate_wallet(filename):
    d = {}
    pk, sk = RK.generate_keys()
    d["pk"], d["sk"]  = str(pk.decode()), str(sk.decode())
    with open(filename, "w") as f:
        json.dump(d, f)
    print("New keys stored in file", filename)

def create_and_send_transaction(recipient, amount):
    if not WALLET:
        print("Load a wallet!")
        return
    T = Transaction(WALLET.public_key, recipient, amount)
    T.sign(WALLET.private_key)
    send_transaction(T)
    print("Transaction sent to Node")

def send_transaction(T):
    '''
    Sends a transaction to a full node
    '''
    pass

def connect_to_fullnode():
    '''
    Connects to a fullnode
    '''
    return None

def main():
    # Connect to a Node
    connection = connect_to_fullnode()
    choice = prompt()
    while choice != "q":
        #try:
        choice = choice.split(" ")
        if choice[0] == "g":
            generate_wallet(choice[1])
        elif choice[0] == "l":
            load_wallet(choice[1])
        elif choice[0] == "t":
            pass
        elif choice[0] == "b":
            pass
        elif choice[0] == "u":
            pass
        else:
            print("Invalid choice")
        #except Exception as e:
        #    print(e)
        choice = prompt()

if __name__=="__main__":
    main()
