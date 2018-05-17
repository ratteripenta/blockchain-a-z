import threading

import requests
from flask import Flask, jsonify, request
from werkzeug.serving import run_simple

from . import chains


class BlockchainApp:

    def __init__(self, host='localhost', port=5000, chain=chains.Blockchain):

        self.host = host
        self.port = port
        self.chain = chain()

        self.host_url = f'http://{self.host}:{self.port}'

        self.app = Flask(__name__)
        self.add_api_endpoints()

        self.thread = threading.Thread(
            target=run_simple,
            kwargs={
                'hostname': self.host,
                'port': self.port,
                'application': self.app}
        )

    def __enter__(self):

        self.start()

        return self

    def __exit__(self, *args):

        self.stop()

    def add_api_endpoints(self):
        "Add API endpoints to the Flask WebApp."

        self.app.add_url_rule(
            rule='/blocks',
            view_func=self.api_blocks,
            methods=['GET', 'POST']
        )
        self.app.add_url_rule(
            rule='/blocks/validate',
            view_func=self.api_validate,
        )
        self.app.add_url_rule(
            rule='/shutdown',
            view_func=self.api_shutdown,
        )

    def api_blocks(self):
        "Either retrieve the node's current chain or post a new block to the chain."

        if request.method == 'POST':

            prev_block = self.chain.get_previous_block()
            prev_hash = self.chain.hash_block(prev_block)
            prev_proof = prev_block['proof']

            proof = self.chain.proof_of_work(prev_proof)

            block = self.chain.create_block(proof, prev_hash)

            response = {'message': 'Congratulations, you just mined a Block!',
                        'block': block}

            return (jsonify(response), 200)

        if request.method == 'GET':

            response = {'blockchain': self.chain.chain,
                        'length': len(self.chain.chain)}

            return (jsonify(response), 200)

    def api_validate(self):
        "Validate the chain"

        if self.chain.is_chain_valid(self.chain.chain):

            response = {'message': 'Chain is valid.',
                        'valid': True}
            return (jsonify(response), 200)

        else:

            response = {'message': 'Chain is not valid!',
                        'valid': False}
            return (jsonify(response), 500)

    def api_shutdown(self):
        "Shutdown the Flask WebApp"

        request.environ.get('werkzeug.server.shutdown')()

        return jsonify({'message': 'Shutting down'}), 200

    def start(self):
        "Start the Flask-based Blockchain WebApp."

        self.thread.start()

    def stop(self):
        "Stop the Flask-based Blockchain WebApp."

        if self.thread.is_alive():

            return requests.get(f'{self.host_url}/shutdown')
