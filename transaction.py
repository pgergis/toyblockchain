import hashlib
import json

from wallet import Keys

class Transaction(object):
    def __init__(self, sender, recipient, previous_transaction):
        self.contents = {
            'sender_pub_key': sender,
            'recipient_pub_key': recipient,
            'previous_transaction': previous_transaction
        }
        self.signature = None
        self.block_index = None

    def set_block(self, block_index):
        self.block_index = block_index

    def sign(self, rsa_keys):
        return rsa_keys.sign(self.hash())

    def hash(self):
        new_hash = hashlib.sha3_256(self.contents['recipient_pub_key'])
        new_hash.update(self.contents['previous_transaction'] or b'')
        return new_hash.digest()
