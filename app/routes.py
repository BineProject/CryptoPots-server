from app import app, monitor
from flask import jsonify
import dataclasses
import json
import configparser


@app.route("/pots/active")
@app.route("/pots")
def activePots():
    return jsonify([dataclasses.asdict(item) for item in monitor.get_pots_data()])


@app.route("/pots/user/<string:user>")
def userPots(user: str):
    return jsonify(
        [dataclasses.asdict(item) for item in monitor.get_user_pots_data(user)]
    )


@app.route("/contract")
@app.route("/contract/address")
def getContractAddress():
    config = configparser.ConfigParser()
    config.read("contracts/data.ini")
    return jsonify(address=config["DEFAULT"]["address"])


@app.route("/contract/abi")
def getContractAbi():
    return jsonify(json.load(open("contracts/CryptoPotsController.json"))["abi"])
