import pymysql
import typing
from util import RawPotData, ParticipantsData


class DataSaver:
    def __init__(self) -> None:
        self.con = pymysql.connect("localhost", "root", "1234", "cryptopots_data")
        self.cur = self.con.cursor()
        self.cur.execute("DROP TABLE IF EXISTS Participations")
        self.cur.execute("DROP TABLE IF EXISTS Participants")
        self.cur.execute("DROP TABLE IF EXISTS Pots")

        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Pots("
            " `id` INT NOT NULL, "
            " `volume` VARCHAR(80) NOT NULL, "
            " `started` TINYINT NULL, "
            " `finished` TINYINT NULL, "
            " `remaining_blocks` INT NULL, "
            " `owner` VARCHAR(80) NOT NULL, "
            " `duration` MEDIUMINT NOT NULL, "
            " PRIMARY KEY (`id`)"
            ")"
        )

        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Participants("
            " `address` VARCHAR(50) NOT NULL, "
            " PRIMARY KEY (`address`)"
            ")"
        )

        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Participations("
            " `participant_address` VARCHAR(50)  NOT NULL, "
            " `pot_id` INT NOT NULL, "
            " `volume` VARCHAR(80) NOT NULL, "
            " PRIMARY KEY (`pot_id`, `participant_address`), "
            " FOREIGN KEY (`participant_address`) "
            "  REFERENCES Partisipants(`address`), "
            " FOREIGN KEY (`pot_id`) "
            "  REFERENCES Pots(`id`)"
            ")"
        )

        self.con.commit()

    def add_pot_data(self, data: RawPotData) -> None:
        self.cur.execute(
            "INSERT INTO Pots VALUES(%s, %s, %s, %s, %s, %s, %s)ON DUPLICATE KEY "
            " UPDATE volume=%s, started=%s, finished=%s, "
            " remaining_blocks=%s, owner=%s, duration=%s",
            (
                data.pot_id,
                *(
                    [
                        data.volume,
                        data.started,
                        data.finished,
                        data.remaining_blocks,
                        data.owner,
                        data.duration,
                    ]
                    * 2
                ),
            ),
        )
        self.con.commit()

    def add_participant_data(self, pot_id: int, participant: str, volume: int) -> None:
        self.cur.execute(
            "INSERT IGNORE INTO Partisipants VALUES(%s)", (participant,),
        )
        self.cur.execute(
            "INSERT INTO Participations(`participant_address`, `pot_id`, `volume`)"
            " VALUES(%s, %s, %s)"
            " ON DUPLICATE KEY"
            " UPDATE `volume` = %s",
            (participant, pot_id, volume, volume),
        )
        self.con.commit()

    def remove_participants_data(self, pot_id: int) -> None:
        self.cur.executemany(
            "DELETE FROM Participations WHERE "
            "`pot_id` = %s AND `participant_address` = %s",
            [
                (pot_id, partisipant)
                for partisipant, _ in self.get_participants_list(pot_id)
            ],
        )

    def get_pots_list(self) -> typing.List[typing.Tuple[typing.Any, ...]]:
        self.cur.execute("SELECT * FROM Pots")
        res = self.cur.fetchall()
        return (
            [typing.cast(typing.Tuple[typing.Any, ...], row) for row in res]
            if res
            else []
        )

    def get_user_pots_list(
        self, owner: str
    ) -> typing.List[typing.Tuple[typing.Any, ...]]:
        self.cur.execute("SELECT * FROM Pots WHERE `owner` = %s", (owner,))
        res = self.cur.fetchall()
        return (
            [typing.cast(typing.Tuple[typing.Any, ...], row) for row in res]
            if res
            else []
        )

    def get_participants_list(self, pot_id: int) -> typing.List[typing.Tuple[str, int]]:
        self.cur.execute(
            "SELECT `participant_address`, `volume` "
            "FROM Participations WHERE `pot_id` = %s",
            (pot_id,),
        )
        res = self.cur.fetchall()
        return [typing.cast(typing.Tuple[str, int], row) for row in res] if res else []
