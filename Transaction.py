#!/usr/bin/env python3
import json
import datetime
from RSA_Keys import RSA_Keys as RK
from Wallet import Wallet

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.tid = datetime.datetime.now()
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = None

    def generate_transaction(Wallet, amount, recipient_key):
        '''
        Uses a wallet to create a transaction

        Takes a public key of a recipient and an amount
        and creates a transaction sending them that amount
        '''
        T = Transaction(Wallet.public_key, recipient_key, amount)
        T.sign(Wallet.secret_key)
        return T

    def verify_transaction(self):
        '''
        Verifys the transcation is valid cryptographicallty by public key of
        sender and signature
        '''
        if not self.signature:
            return False
        return RK.verify(self.sender, self.to_string(False), self.signature)

    def sign(self, sk):
        '''
        Signs transaction with secret key
        '''
        self.signature = RK.sign(sk, self.to_string(False))
        return self.signature


    def to_json(self, sig=True):
        '''
        Returns a json of the transaction
        '''
        j = {}
        j["Transaction_ID"]         = str(self.tid)
        j["Sender_Public_Key"]      = str(self.sender)
        j["Recipient_Public_Key"]   = str(self.recipient)
        j["Amount"]                 = str(self.amount)
        if self.signature and sig:
            j["Signature"] = str(self.signature)
        return j

    def to_string(self, sig=True):
        '''
        Makes the json of the transcation a string
        '''
        return json.dumps(self.to_json(sig))

if __name__=="__main__":
    # Testing
    w1 = Wallet(RK.generate_keys())
    w2 = Wallet(RK.generate_keys())

    T = Transaction.generate_transaction(w1, 10, w2.public_key)
    print(T.verify_transaction())
