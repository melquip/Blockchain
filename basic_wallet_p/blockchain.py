import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS


class Blockchain(object):
    def __init__(self):
        self.miners = []
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain
        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the block to the chain
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block
        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        # Use hashlib.sha256 to create a hash
        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand
        
        # Return the hashed block string in hexadecimal format
        return hashlib.sha256(block_string).hexdigest()

    def new_transaction(self, sender, recipient, amount):
        """
        Create a method in the `Blockchain` class called `new_transaction` 
        that adds a new transaction to the list of transactions:
        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the `block` that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        # set a initial guess concatonate block string and proof then encode them
        guess = f"{block_string}{proof}".encode()
        # create a guess hash and hexdigest it
        guess_hash = hashlib.sha256(guess).hexdigest()
        # then return True if the guess hash has the valid number of leading zeros otherwise return False
        return guess_hash[:6] == "000000"



# Instantiate our Node
app = Flask(__name__)
CORS(app)
# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['POST'])
def mine():
    # Run the proof of work algorithm to get the next proof
    data = request.get_json()

    required = ['proof', 'id']

    # if the values from data are not in required
    if not all(k in data for k in required):
        # then send a json message of missing values
        response = {'message': "Missing Values"}
        # return a 400 error
        return jsonify(response), 400
    
    # get the submitted proof from data
    submitted_proof = data.get('proof')

    # determine if proof is valid
    last_block = blockchain.last_block
    last_block_string = json.dumps(last_block, sort_keys=True)
    if blockchain.valid_proof(last_block_string, submitted_proof):
        # forge the new block
        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(submitted_proof, previous_hash)
        # build a response dictionary

        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash']
        }
        # return the response
        return jsonify(response), 200
    # otherwise
    else:
        # send a json mesage that the proof was invalid
        response = { 'message': "Proof was invalid or already submitted"}
        return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        "length": len(blockchain.chain),
        "chain": blockchain.chain
    }
    return jsonify(response), 200

@app.route('/last_block', methods=['GET'])
def last_block():
    response = { 'last_block': blockchain.last_block }
    return jsonify(response), 200

@app.route('/user/change', methods=['POST'])
def change_username():
    data = request.get_json()
    if not data['lastUsername'] or not data['username']:
        return jsonify({ 'message': 'Missing fields' }), 400
    if data['username'] in blockchain.miners:
        return jsonify({ 'message': 'Username already taken' }), 400

    lastUsername = data['lastUsername']
    username = data['username']

    for b in range(0, len(blockchain.chain)):
        for t in range(0, len(blockchain.chain[b]['transactions'])):
            currTransaction = blockchain.chain[b]['transactions'][t]
            if currTransaction.sender == lastUsername:
                blockchain.chain[b]['transactions'][t].sender = username
            if currTransaction.receiver == lastUsername:
                blockchain.chain[b]['transactions'][t].receiver = username

    return jsonify({ 'success': True }), 200


@app.route('/user/balance', methods=['POST'])
def get_user_balance():
    data = request.get_json()
    if not data['username']:
        return jsonify({ 'message': 'Missing fields' }), 400

    username = data['username']
    balance = 0

    for b in range(0, len(blockchain.chain)):
        for t in range(0, len(blockchain.chain[b]['transactions'])):
            currTransaction = blockchain.chain[b]['transactions'][t]
            if currTransaction.sender == username:
                balance -= currTransaction.amount
            if currTransaction.receiver == username:
                balance += currTransaction.amount

    return jsonify({ 'username': username, 'balance': balance }), 200

@app.route('/user/transactions', methods=['POST'])
def get_user_transactions():
    data = request.get_json()
    if not data['username']:
        return jsonify({ 'message': 'Missing fields' }), 400

    username = data['username']
    transactions = []
    for b in range(0, len(blockchain.chain)):
        for t in range(0, len(blockchain.chain[b]['transactions'])):
            currTransaction = blockchain.chain[b]['transactions'][t]
            if currTransaction.sender == username or currTransaction.receiver == username:
                transactions.append(currTransaction)

    return jsonify({ 'transactions': transactions }), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in data for k in required):
        return jsonify({ 'message': 'Missing values' }), 400
    
    index = blockchain.new_transaction(data['sender'], data['recipient'], data['amount'])
    return jsonify({ 'message': f'Transaction will be added to Block {index}' }), 201
    
# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)