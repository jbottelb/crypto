#!/usr/bin/env python3
import json
import datetime
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.tid = datetime.datetime.now()
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = None

    def verify_transaction(self):
        pass

    def sign(self, signer):
        t = SHA256.new(self.to_json().encode())
        self.signature = signer.sign(t)
        return self.signature


    def to_json(self):
        j = {}
        j["tid"] = str(self.tid)
        j["sender"] = str(self.sender)
        j["recipient"] = str(self.recipient)
        j["amount"] = str(self.amount)
        if self.signature:
            j["signature"] = str(self.signature)

        return json.dumps(j)

    def __str__(self):
        return str(to_json(self))

if __name__=="__main__":
    key = RSA.generate(4096)
    public_key = key.publickey().exportKey('PEM')
    private_key = key.exportKey('PEM')
    signer = PKCS1_v1_5.new(key)

    t = Transaction(public_key, "anything", 5)
    t.sign(signer)
    print(t.to_json())
