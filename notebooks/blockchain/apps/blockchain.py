import threading
import requests

from flask import Flask, request, jsonify

from ..chains import Blockchain

blockchain_app = Flask(__name__)
blockchain = Blockchain()


@blockchain_app.route('/blocks', methods=['GET', 'POST'])
def blocks():

    if request.method == 'POST':

        prev_block = blockchain.get_previous_block()
        prev_hash = blockchain.hash_block(prev_block)
        prev_proof = prev_block['proof']

        proof = blockchain.proof_of_work(prev_proof)

        block = blockchain.create_block(proof, prev_hash)

        response = {
            'message': 'Congratulations, you just mined a Block!',
            'block': block
        }

        return (jsonify(response), 200)

    if request.method == 'GET':

        response = {
            'blockchain': blockchain.chain,
            'length': len(blockchain.chain),
        }

        return (jsonify(response), 200)


@blockchain_app.route('/blocks/validate', methods=['GET'])
def validate():

    if blockchain.is_chain_valid(blockchain.chain):

        response = {
            'message': 'Chain is valid.',
            'valid': True
        }
        return (jsonify(response), 200)

    response = {
        'message': 'Chain is not valid!',
        'valid': False
    }
    return (jsonify(response), 500)


@blockchain_app.route('/shutdown')
def shutdown():

    request.environ.get('werkzeug.server.shutdown')()

    return jsonify({'message': 'Shutting down'}), 200


class BlockchainApp:

    def __init__(self):

        self.host = 'localhost'
        self.port = 5000
        self.host_url = 'http://{}:{}'.format(self.host, self.port)
        self.thread = threading.Thread(
            target=blockchain_app.run,
            kwargs={'host': self.host, 'port': self.port})

    def start(self):
        self.thread.start()

    def stop(self):
        if self.thread.is_alive():
            return requests.get('{}/shutdown'.format(self.host_url))

    def mine_block(self):
        return requests.post('{}/blocks'.format(self.host_url))

    def get_blockchain(self):
        return requests.get('{}/blocks'.format(self.host_url))

    def validate_blockchain(self):
        return requests.get('{}/blocks/validate'.format(self.host_url))

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
