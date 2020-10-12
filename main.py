from contract_monitor import load_contracts_data
from contract_monitor import load_contracts_data
from app import app
from database import DataSaver

saver = DataSaver()

for pot_data in load_contracts_data():
    saver.add_pot_data(
        pot_id=pot_data["pot_id"],
        volume=pot_data["volume"],
        started=pot_data["started"],
        finished=pot_data["finished"],
        remaining_blocks=pot_data["remaining_blocks"],
    )

