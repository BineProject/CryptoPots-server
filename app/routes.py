from app import app, monitor
from flask import jsonify, abort
import dataclasses
import json
import configparser


# @app.errorhandler(404)
# def notFound():
#     return (
#         jsonify({"err": 404, "msg": "The stuff you requested for is not found."}),
#         404,
#     )


@app.route("/pots/active")
@app.route("/pots")
def activePots():
    return jsonify([dataclasses.asdict(item) for item in monitor.get_pots_data()])


@app.route("/pots/user/<string:user>")
def userPots(user: str):
    return jsonify(
        [dataclasses.asdict(item) for item in monitor.get_user_pots_data(user)]
    )


@app.route("/pot/<int:pot_id>")
def potData(pot_id: int):
    pot_data = monitor.get_pot_data(pot_id)
    if not pot_data:
        abort(404)
    return jsonify(dataclasses.asdict(pot_data))


@app.route("/contract")
@app.route("/contract/address")
def getContractAddress():
    config = configparser.ConfigParser()
    config.read("contracts/data.ini")
    return jsonify(address=config["DEFAULT"]["address"])


@app.route("/contract/abi")
def getContractAbi():
    return jsonify(json.load(open("contracts/CryptoPotsController.json"))["abi"])
