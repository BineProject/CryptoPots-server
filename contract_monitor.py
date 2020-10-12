import json
import typing
from web3 import Web3, HTTPProvider
from web3.logs import STRICT

__all__ = ["load_contracts_data", "ContractData"]

# truffle development blockchain address
blockchain_address = "HTTP://127.0.0.1:8545"
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))
# Set the default account
# (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[1]

# Path to the compiled contract JSON file
compiled_contract_path = "contracts/CryptoPotsController.json"
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = "0xDD447A7f39048790F57AEC3Acc3c940464038Ed1"

with open(compiled_contract_path) as file:
    # load contract info as JSON
    contract_json = json.load(file)
    # fetch contract's abi - necessary to call its functions
    contract_abi = contract_json["abi"]

# Fetch deployed contract reference
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)


class ContractData(typing.TypedDict):
    pot_id: int
    volume: int
    started: bool
    finished: bool
    remaining_blocks: int
    partisipants: typing.Dict[str, int]


def load_contracts_data() -> typing.List[ContractData]:
    return [
        {
            "pot_id": pot_id,
            "volume": contract.functions.getPotVolume(pot_id).call(),
            "started": contract.functions.isPotStarted(pot_id).call(),
            "finished": contract.functions.isPotFinished(pot_id).call(),
            "remaining_blocks": contract.functions.remainingBlocks(pot_id).call(),
            "partisipants": {
                partisipant: contract.functions.getParticipantBet(
                    pot_id, partisipant
                ).call()
                for partisipant in contract.functions.getParticipants(pot_id).call()
            },
        }
        for pot_id in contract.functions.getActivePotsIDs().call()
    ]
