from textwrap import dedent
from flask import Flask, jsonify, request
import sys

import node


# Instantiate our Node
app = Flask(__name__)

# Instantiate the Blockchain
node = node.Node()

@app.route('/mine', methods=['GET'])
def mine():
    response = node.mine()
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'd data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = node.process_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'We\'ll attempt to put this into Block {index}, but it might end up being later...'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': node.blockchain.blocks,
        'length': len(node.blockchain.blocks),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_neighbors():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    response = node.register_neighbors(nodes)

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = node.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': node.blockchain.blocks,
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': node.blockchain.blocks,
        }

    return jsonify(response), 200

def run(port):
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    print("Run on port: ", end='')
    if sys.argc == 1:
        port = sys.argv[1]
    else:
        port = int(input())
    run(port)
