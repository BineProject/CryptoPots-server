import typing
import dataclasses


@dataclasses.dataclass
class RawPotData:
    pot_id: int
    volume: int
    started: bool
    finished: bool
    remaining_blocks: int
    owner: str
    duration: int


ParticipantsData = typing.Dict[str, int]


@dataclasses.dataclass
class FullPotData(RawPotData):
    participants: ParticipantsData

