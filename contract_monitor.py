from dataclasses import dataclass
import json
import threading
import typing
from util.types import FullPotData
from web3 import Web3, HTTPProvider
from web3.logs import STRICT
from database import DataSaver
from util import RawPotData, FullPotData, ParticipantsData


class Event(typing.TypedDict):
    args: typing.Mapping[str, typing.Any]


class IEventFilter(typing.Protocol):
    def get_new_entries(self) -> typing.List[Event]:
        ...


class Monitor:
    def __init__(self, saver: DataSaver) -> None:
        # truffle development blockchain address
        self.blockchain_address = "HTTP://127.0.0.1:8545"
        # Client instance to interact with the blockchain
        self.web3 = Web3(HTTPProvider(self.blockchain_address))
        # Set the default account
        # (so we don't need to set the "from" for every transaction call)
        self.web3.eth.defaultAccount = self.web3.eth.accounts[1]

        # Path to the compiled contract JSON file
        self.compiled_contract_path = "contracts/CryptoPotsController.json"
        # Deployed contract address (see `migrate` command output: `contract address`)
        self.deployed_contract_address = "0x6b3F7bccdabe3f2A600610F1fFb354C9f7462b10"

        with open(self.compiled_contract_path) as file:
            # load contract info as JSON
            contract_json = json.load(file)
            # fetch contract's abi - necessary to call its functions
            contract_abi = contract_json["abi"]

        # Fetch deployed contract reference
        self.contract = self.web3.eth.contract(
            address=self.deployed_contract_address, abi=contract_abi
        )
        self.saver = saver

        self.__load_initial_data()
        self.__init_event_system()

    def __init_event_system(self) -> None:
        self._filter_connections: typing.Dict[IEventFilter, typing.Callable] = {}

        def connect_event(event: str, fromBlock: str, *args, **kwargs):
            def connect_event_decorator(func: typing.Callable) -> typing.Callable:
                self._filter_connections[
                    getattr(self.contract.events, event).createFilter(
                        fromBlock=fromBlock, *args, **kwargs
                    )
                ] = func
                return func

            return connect_event_decorator

        @connect_event("newPotCreated", fromBlock="latest")
        def _on_new_pot_created(id: int, creator: str, **kwargs) -> None:
            # print("newPotCreated", id, creator)
            self.saver.add_pot_data(self._load_pot_data(id))

        @connect_event("BetLog", fromBlock="latest")
        def _on_new_bet_made(
            potID: int, who: str, amount: int, aggregatedAmount: int, **kwargs
        ) -> None:
            # print("BetLog", potID, who, amount)
            self.saver.add_pot_data(self._load_pot_data(potID))
            self.saver.add_participant_data(potID, who, aggregatedAmount)

        @connect_event("PayoutLog", fromBlock="latest")
        def _on_new_payout_made(
            potID: int, who: str, amount: int, data: str, **kwargs
        ) -> None:
            # print("PayoutLog", potID, who, amount, data)
            self.saver.add_pot_data(self._load_pot_data(potID))
            self.saver.remove_participants_data(potID)

        def _run_event_loop() -> None:
            while True:
                for event_filter, callback in self._filter_connections.items():
                    for event in event_filter.get_new_entries():
                        callback(**dict(event["args"]))

        self.thread = threading.Thread(target=_run_event_loop)
        self.thread.setDaemon(True)
        self.thread.start()

    def __load_initial_data(self) -> None:
        for pot_data in self._load_pots_data():
            self.saver.add_pot_data(pot_data)
            for partisipant, volume in self._load_participants_data(
                pot_data.pot_id
            ).items():
                self.saver.add_participant_data(pot_data.pot_id, partisipant, volume)

    def _load_pots_data(self) -> typing.List[RawPotData]:
        return [
            self._load_pot_data(pot_id)
            for pot_id in self.contract.functions.getActivePotsIDs().call()
        ]

    def _load_pot_data(self, pot_id: int) -> RawPotData:
        return RawPotData(
            pot_id=pot_id,
            volume=self.contract.functions.getPotVolume(pot_id).call(),
            started=self.contract.functions.isPotStarted(pot_id).call(),
            finished=self.contract.functions.isPotFinished(pot_id).call(),
            remaining_blocks=self.contract.functions.remainingBlocks(pot_id).call(),
            owner=self.contract.functions.getPotOwner(pot_id).call(),
            duration=self.contract.functions.getPotDuration(pot_id).call(),
        )

    def _load_participants_data(self, pot_id: int) -> ParticipantsData:
        return {
            typing.cast(str, partisipant): typing.cast(
                int,
                self.contract.functions.getParticipantBet(pot_id, partisipant).call(),
            )
            for partisipant in self.contract.functions.getParticipants(pot_id).call()
        }

    _RowDataType = typing.Tuple[int, int, bool, bool, int, str, int]

    def get_pots_data(self) -> typing.List[FullPotData]:
        data: typing.List[Monitor._RowDataType] = typing.cast(
            typing.List[Monitor._RowDataType], self.saver.get_pots_list()
        )
        return [
            FullPotData(
                *pot, participants=dict(self.saver.get_participants_list(pot[0]))
            )
            for pot in data
        ]

    def get_user_pots_data(self, owner: str) -> typing.List[FullPotData]:
        data: typing.List[Monitor._RowDataType] = typing.cast(
            typing.List[Monitor._RowDataType], self.saver.get_user_pots_list(owner)
        )
        return [
            FullPotData(
                *pot, participants=dict(self.saver.get_participants_list(pot[0]))
            )
            for pot in data
        ]
