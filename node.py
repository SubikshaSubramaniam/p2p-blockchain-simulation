from flask import Flask, jsonify, request, render_template, redirect, url_for
from uuid import uuid4
from blockchain import Blockchain

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html', chain=blockchain.chain, peers=list(blockchain.nodes))

@app.route('/mine', methods=['POST'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block['proof'])
    blockchain.new_transaction(sender="0", recipient=node_identifier, certificate="Mining Reward")
    block = blockchain.new_block(proof, blockchain.hash(last_block))
    return redirect(url_for('index'))

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    required = ['sender', 'recipient', 'certificate']
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['certificate'])
    return redirect(url_for('index'))

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    nodes = request.form['nodes'].split(',')
    for node in nodes:
        blockchain.register_node(node)
    return redirect(url_for('index'))

@app.route('/nodes/resolve', methods=['POST'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    return redirect(url_for('index'))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int)
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)
