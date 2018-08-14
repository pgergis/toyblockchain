from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15 as sig
from Crypto.Cipher import PKCS1_OAEP as ciph
import hashlib

class Keys(object):
    def __init__(self):
        self.rsa_keys = RSA.generate(2048)
        self.key_cipher = ciph.new(self.rsa_keys)
        self.key_sigs = sig.new(self.rsa_keys)

    def public_key(self):
        return self.rsa_keys.publickey().export_key()

    def encrypt(self, message):
        return self.key_cipher.encrypt(message)

    def decrypt(self, ciphertext):
        return self.key_cipher.decrypt(ciphertext)

    def sign(self, message):
        mes_hash = hashlib.sha3_256(message).digest()
        return self.key_sigs.sign(mes_hash)

class Wallet(object):
    def __init__(self):
        self.keys = Keys()
        self.amount = 0
        self.received_txns = []

    def public_key(self):
        return self.keys.public_key()

    def send_payment(self, amount, recipient, node):
        if amount > len(self.received_txns):
            fail
        else:
            signed_coins = []
            for _ in range(0, amount):
                previous_txn = self.received_txns.pop()
                txn = {
                    "sender": sender,
                    "recipient": recipient,
                    "previous_txn": previous_txn
                }

                txn_hash = hashlib.sha3_256(recipient)
                txn_hash.update(previous_txn)
                signed_coins.append((txn, keys.sign(txn_hash)))
            node.process_transaction(self.keys.public_key, recipient, amount, signed_coins)
