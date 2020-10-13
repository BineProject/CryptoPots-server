from app import app, monitor
from flask import jsonify
from flask_cors import cross_origin
import dataclasses


@app.route("/activePots")
@cross_origin()
def activePots():
    return jsonify([dataclasses.asdict(item) for item in monitor.get_pots_data()])


@app.route("/userPots/<string:user>")
@cross_origin()
def userPots(user: str):
    return jsonify(
        [dataclasses.asdict(item) for item in monitor.get_user_pots_data(user)]
    )

