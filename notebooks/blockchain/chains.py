import datetime
import hashlib
import json
from urllib.parse import urlparse
from uuid import uuid4

import requests


class Blockchain:

    def __init__(self):

        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        "Create a block."

        block = {
            'index': len(self.chain),
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
        }

        self.chain.append(block)

        return block

    def get_previous_block(self):

        return self.chain[-1]

    def hash_proof(self, previous_proof, next_proof):
        "Calculate the SHA256-hash"

        return (hashlib
                .sha256(str(next_proof**2 - previous_proof**2).encode())
                .hexdigest())

    def hash_block(self, block):
        "Calculate the SHA256-hash for a block."

        encoded_block = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, previous_proof):
        "Calculate a new proof related to the previous block."

        next_proof = 1
        check_proof = False

        while check_proof is False:

            if self.hash_proof(previous_proof, next_proof)[:4] == '0000':
                check_proof = True

            else:
                next_proof += 1

        return next_proof

    def is_chain_valid(self, chain):
        "Validate that block and proof hashes are correct across the chain."

        for i in range(len(chain)):

            if i == 0:
                continue

            if chain[i]['previous_hash'] != self.hash_block(chain[i - 1]):
                return False

            previous_proof = chain[i - 1]['proof']
            next_proof = chain[i]['proof']

            if self.hash_proof(previous_proof, next_proof)[:4] != '0000':

                return False

            return True


class GeneralCoin(Blockchain):

    def __init__(self):

        self.node_address = str(uuid4()).replace('-', '')
        self.transactions = []
        self.nodes = set()
        super().__init__()

    def create_block(self, proof, previous_hash):
        "Create a block with new transactions."

        block = {
            'index': len(self.chain),
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)

        return block

    def add_transaction(self, sender, receiver, amount):
        "Add a transaction to the list of transactions."

        self.transactions.append(
            {'sender': sender,
             'receiver': receiver,
             'amount': amount})

        return self.get_previous_block()['index'] + 1

    def add_node(self, address):
        "Add a node to the GeneralCoin network."

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        "Scan the network for longest chain and replace the current accordingly."

        longest_chain = None
        longest_chain_length = len(self.chain)

        for node in self.nodes:

            response = requests.get(f'http://{node}/blocks')

            if not response.status_code == 200:

                print(f'Bad response from {node}: {response.status_code}')
                continue

            node_chain = response.json()['chain']
            node_chain_length = response.json()['length']

            if node_chain_length > longest_chain_length and self.is_chain_valid(node_chain):

                longest_chain_length = node_chain_length
                longest_chain = node_chain

        if longest_chain is not None:

            self.chain = longest_chain

            return True

        return False
