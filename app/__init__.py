from flask import Flask
from contract_monitor import Monitor
from database import DataSaver

app = Flask(__name__)
saver = DataSaver()
monitor = Monitor(saver)

from . import routes
