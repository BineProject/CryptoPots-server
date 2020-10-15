from app import app, monitor
from flask import jsonify
import dataclasses


@app.route("/pots/active")
@app.route("/pots")
def activePots():
    return jsonify([dataclasses.asdict(item) for item in monitor.get_pots_data()])


@app.route("/pots/user/<string:user>")
def userPots(user: str):
    return jsonify(
        [dataclasses.asdict(item) for item in monitor.get_user_pots_data(user)]
    )

