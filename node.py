import requests
from urllib.parse import urlparse
from uuid import uuid4

from blockchain import Blockchain
from wallet import Wallet, Keys

class Node(object):
    def __init__(self, wallet=Wallet()):
        self.neighbors = set()
        self.blockchain = Blockchain()
        self.wallet = wallet
        # Generate a globally unique address for this node
        self.node_identifier = str(uuid4()).replace('-', '')
        self.current_transactions = []

    def mine(self):
        # We run the proof of work algorithm to get the next proof
        last_block = self.blockchain.last_block
        last_proof = last_block['proof']
        proof = self.proof_of_work(last_proof)

        # We must receive a reward for finding the proof.
        # The sender is '0' to signify that this node has mined a new coin.
        self.process_transaction(
            sender = "0",
            recipient = self.wallet.public_key(),
            amount = 1,
        )

        # Forge the new Block by adding it to the chain
        previous_hash = self.blockchain.hash(last_block)
        block = self.blockchain.new_block(self.current_transactions, proof, previous_hash)
        # Reset txns to avoid double adds (TODO: Handle failed adds after consensus check)
        self.current_transactions = []

        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }

        return response

    def process_transaction(self, sender, recipient, amount, signed_coins):
        # Adds a new transaction to the list of transactions
        """
        Creates a new transaction to go into the next mined Block

        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        if amount != len(coins):
            raise Exception('txn amount not equal to coins signed by sender')

        valid_coins = [coin for coin in signed_coins if self.blockchain.valid_coin(coin)]

        for coin in valid_coins:
            self.transact_coin(recipient)

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.blockchain.last_block['index'] + 1

    def register_neighbors(self, nodes):
        """
        Add new nodes to the list of nodes

        :param nodes: <list><str> Addressof node. e.g., 'http:/192.168.0.5:5000'
        :return: <dict> List of neighbor nodes
        """

        for node in nodes:
            self.neighbors.add(urlparse(node).netloc)

        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(self.neighbors),
        }
        return response

    def proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof

        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while Blockchain.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    def resolve_conflicts(self):
        """
        This is the Consensus Algorithm. It resolve conflicts
        by replacing our chain with the longest on the network.

        :return: <bool> True if our chain was replaced, False if not
        """

        neighbors = self.neighbors
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.blockchain.blocks)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and blockchain.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.blockchain.blocks = new_chain
            return True

        return False
