#!/usr/bin/env python3
'''
Class to handle a wallet with RSA keys
'''

class Wallet:
    def __init__(self, keys):
        pk, sk = keys
        self.secret_key = sk
        self.public_key = pk
        balance = None

    def update_balance(self, amount):
        self.balance = amount

    def change_balance(self, amount):
        self.balance += amount
        return self.balance
