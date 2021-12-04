#!/usr/bin/env python3
'''
Handles generating RSA keys, signing messages and verifying them
'''
from base64 import b64encode
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import random

class RSA_Keys:
    def generate_keys():
        '''
        Generates and returns RSA keys
        Reurns a public private key pair
        '''
        new_key = RSA.generate(2048, e=65537)
        public_key = new_key.publickey().exportKey("PEM")
        private_key = new_key.exportKey("PEM")
        return public_key, private_key

    def sign(secret_key: str, message: str):
        '''
        Uses the private key to sign the message
        '''
        digest = SHA256.new(message.encode())
        return pkcs1_15.new(RSA.import_key(secret_key)).sign(digest)

    def verify(public_key: str, message: str, signature: str):
        '''
        Uses public key to verify a transaction
        Returns True on valid and False on invalid
        '''
        digest = SHA256.new(message.encode())
        try:
            pkcs1_15.new(RSA.import_key(public_key)).verify(digest, signature)
        except Exception as e:
            return False
        return True


if __name__ == "__main__":
    '''
    Test cases for keys
    '''
    pk, sk = RSA_Keys.generate_keys()
    message = "test message"
    sig = RSA_Keys.sign(sk, message)
    # Verify good message
    print(RSA_Keys.verify(pk, message, sig))
    # Alter the signature
    print(RSA_Keys.verify(pk, message, sig + b"bad"))
    # Alter the Message
    print(RSA_Keys.verify(pk, message + "bad", sig))
