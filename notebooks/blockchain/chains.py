import datetime
import hashlib
import json


class Blockchain:

    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
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
