import datetime
import hashlib
import json
from flask import Flask, jsonify


class BlockChain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1, prev_hash="0") # Genesis block i.e. the first block

    def create_block(self, proof, prev_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": prev_hash,
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(
                str(new_proof ** 2 - prev_proof ** 2).encode()
            ).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def is_chain_valid(self, chain):

        prev_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            current_block = chain[block_index]
            if current_block is not None and current_block[
                "previous_hash"
            ] != self.hash(prev_block):
                return False
            prev_proof = prev_block["proof"]
            current_block_proof = current_block["proof"]
            hash_operation = hashlib.sha256(
                str(current_block_proof ** 2 - prev_proof ** 2).encode()
            ).hexdigest()

            if hash_operation[:4] != "0000":
                return False
            prev_block = chain[block_index]
            block_index += 1

        return True


app = Flask(__name__)  # Flask server init

blockchain = BlockChain()  # blockchain object


@app.route("/", methods=["GET"])
def base_url():
    return "Hello World!"


@app.route("/mine_block", methods=["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block["proof"]
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    new_mined_block = blockchain.create_block(proof, previous_hash)
    response = {"message": "You have successfully mined one block.", **new_mined_block}

    return jsonify(response), 200


@app.route("/get_blockchain", methods=["GET"])
def get_blockchain():

    response = {"chain": blockchain.chain, "no of blocks": len(blockchain.chain)}
    return response, 200


@app.route("/is_valid", methods=["GET"])
def is_blockchain_valid():

    message = (
        "Chain is valid !"
        if blockchain.is_chain_valid(blockchain.chain)
        else "Chain is NOT valid !! "
    )
    return {"message": message}, 200

    


app.run("0.0.0.0", 8800)
