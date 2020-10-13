from flask import Flask
from flask_cors import CORS
from contract_monitor import Monitor
from database import DataSaver

app = Flask(__name__)
cors = CORS(app)

saver = DataSaver()
monitor = Monitor(saver)

from . import routes
