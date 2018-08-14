# Toy Blockchain for learning, tutorial here: https://hackernoon.com/learn-blockchains-by-building-one-117428612f46

from collections import Counter
import hashlib
import json
from time import time

from transaction import Transaction

class Blockchain(object):
    def __init__(self):
        self.blocks = []

        # Create the genesis block
        self.new_block([], previous_hash=1, proof=100)

    def new_block(self, new_transactions, proof, previous_hash=None):
        # Creates a new Block and adds it to the chain
        """
        Create a new Block in the Blockchain

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of the previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.blocks)+1,
            'timestamp': time(),
            'transactions': new_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.blocks[-1]),
        }

        self.blocks.append(block)
        return block

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        seen_prev_txns = set()
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            # Check that each transaction is correct
            for txn in block['transactions']:
                if not self.valid_transaction(txn):
                    return False

            last_block = block
            current_index += 1

        return True

    @staticmethod
    def hash(block):
        # Hashes a Block
        """
        Creates a SHA-256 hash of a Block

        :param block: <dict> Block
        :return: <str>
        """

        # We must make sure that the dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Returns the last Block in the chain
        return self.blocks[-1]

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def valid_signature(public_key, message, signature):
        # TODO: implement!
        return True

    def valid_transaction(self, cur_txn):
        if not Blockchain.valid_signature(cur_txn.contents['sender_pub_key'], cur_txn.hash(), cur_txn.signature):
            return False

        # If previous tx is None, check if transaction is first in block
        if cur_txn.contents['previous_transaction'] is None:
            cur_block = self.blocks[cur_txn.block_index]
            return cur_block['transactions'][0].hash() == cur_txn.hash()

        actual_previous_txn = None
        seen_parent_txns = Counter()
        for block in self.chain:
            for txn in block['transactions']:
                seen_parent_txns[txn.contents['previous_transaction']] += 1
                if cur_txn.contents['previous_transaction'] == txn.hash():
                    actual_previous_txn = txn

        is_double_spend = seen_parent_txns[cur_txn.contents['previous_transaction']] > 1

        if is_double_spend: return False

        if {
                actual_previous_txn == None
                or actual_previous_txn.contents['recipient_pub_key'] != cur_txn['sender_pub_key']
        }: return False

        return True
