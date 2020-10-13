from app import app, monitor
from flask import jsonify
import dataclasses


@app.route("/getActivePots")
def home():
    return jsonify([dataclasses.asdict(item) for item in monitor.get_pots_data()])
