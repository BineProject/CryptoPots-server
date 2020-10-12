from app import app
from contract_monitor import load_contracts_data


@app.route("/getActivePots")
def home() -> str:
    d = load_contracts_data()
    return f"{d} : {d.__class__.__name__}"
