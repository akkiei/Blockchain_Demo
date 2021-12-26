#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 19:32:43 2021

@author: akash
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


class BlockChain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, prev_hash="0")
        self.nodes = set()

    def create_block(self, proof, prev_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": prev_hash,
            "transactions": self.transactions,
        }
        self.transactions = []
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

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append(
            {"sender": sender, "receiver": receiver, "amount": amount}
        )
        prev_block = self.get_previous_block()
        return prev_block["index"] + 1

    def add_node(self, address_node):
        parsed_url = urlparse(address_node)
        self.nodes.add(parsed_url.netloc)

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

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/get_blockchain")
            if response.status_code == 200:
                length_of_chain = response.json()["no_of_blocks"]
                blockchain_node = response.json()["chain"]
                if length_of_chain > max_length and self.is_chain_valid(
                    blockchain_node
                ):
                    longest_chain = blockchain_node
                    max_length = length_of_chain

        if longest_chain is not None:
            self.chain = longest_chain
            return True
        return False


app = Flask(__name__)  # Flask server init

node_address = str(uuid4()).replace("-", "")  # address for the node on port 8800

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
    blockchain.add_transaction(node_address, "AkashD", 10)  # 10 coins for mining
    new_mined_block = blockchain.create_block(proof, previous_hash)
    new_mined_block["transactions"] = new_mined_block["transactions"]

    response = {"message": "You have successfully mined one block.", **new_mined_block}

    return jsonify(response), 200


@app.route("/get_blockchain", methods=["GET"])
def get_blockchain():

    response = {"chain": blockchain.chain, "no_of_blocks": len(blockchain.chain)}
    return jsonify(response), 200


@app.route("/is_valid", methods=["GET"])
def is_blockchain_valid():

    message = (
        "Chain is valid !"
        if blockchain.is_chain_valid(blockchain.chain)
        else "Chain is NOT valid !! "
    )
    return jsonify({"message": message}), 200


@app.route("add_trxn", methods=["POST"])
def add_transaction():
    req_body = request.get_json()
    sender = req_body["sender"]
    receiver = req_body["receiver"]
    amount = req_body["amount"]
    if not sender or not receiver or not amount:
        return {"message": "There's error in req body"}, 400

    index = blockchain.add_transaction(sender, receiver, amount)
    return (
        jsonify(
            {"message": f"Trxn added successfully to the block {index}", **req_body}
        ),
        201,
    )


@app.route("connect_node", methods=["POST"])
def connect_new_node():
    req_body = request.get_json()
    nodes = req_body.get("nodes")
    if nodes is None:
        return jsonify({"message": "No Nodes were added!"}), 400
    for node in nodes:
        blockchain.add_node(node)

    return (
        jsonify(
            {
                "message": f"{len(nodes)} nodes were added!",
                "total_nodes": blockchain.nodes,
            }
        ),
        201,
    )


# replace the chain with longest chain
@app.route("/replace_chain", methods=["GET"])
def replace_chain(self):
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced is True:
        return (
            jsonify(
                {"message": "The chain was replaced !!", "new_chain": blockchain.chain}
            ),
            200,
        )
    return (
        jsonify(
            {
                "message": "The chain was NOT replaced !!",
                "current_chain": blockchain.chain,
            }
        ),
        200,
    )


app.run("0.0.0.0", 8800)
