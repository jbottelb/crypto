#!/usr/bin/env python3
'''
Generates a json file with some wallet constants
'''

from RSA_Keys import RSA_Keys as RK
from Wallet import Wallet
import json

def itemize_wallet(wallet):
    return [str(wallet.public_key.decode()), str(wallet.secret_key.decode())]

wallets = {}

wallets["Josh"] = itemize_wallet(Wallet(RK.generate_keys()))
wallets["Brad"] = itemize_wallet(Wallet(RK.generate_keys()))
wallets["John"] = itemize_wallet(Wallet(RK.generate_keys()))
wallets["Mary"] = itemize_wallet(Wallet(RK.generate_keys()))

for i in range(10):
    wallets[str("Client " + str(i))] = itemize_wallet(Wallet(RK.generate_keys()))

with open("wallets.json", "w") as f:
    json.dump(wallets, f)
