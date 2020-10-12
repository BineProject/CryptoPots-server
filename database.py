import pymysql


class DataSaver:
    def __init__(self) -> None:
        self.con = pymysql.connect("localhost", "root", "1234", "cryptopots_data")
        self.cur = self.con.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Pots("
            " `id` INT NOT NULL, "
            " `volume` VARCHAR(80) NOT NULL, "
            " `started` TINYINT NULL, "
            " `finished` TINYINT NULL, "
            " `remaining_blocks` INT NULL, "
            " PRIMARY KEY (`id`)"
            ")"
        )
        self.cur.execute("DELETE FROM Pots")

        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Partisipants("
            " `address` VARCHAR(50) NOT NULL, "
            " PRIMARY KEY (`address`)"
            ")"
        )
        self.cur.execute("DELETE FROM Partisipants")

        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS Participations("
            " `id` INT NOT NULL, "
            " `partisipant_address` VARCHAR(50)  NOT NULL, "
            " `pot_id` INT NOT NULL, "
            " `volume` VARCHAR(80) NOT NULL, "
            " PRIMARY KEY (`id`), "
            " FOREIGN KEY (`partisipant_address`) "
            "  REFERENCES Partisipants(`address`), "
            " FOREIGN KEY (`pot_id`) "
            "  REFERENCES Pots(`id`)"
            ")"
        )
        self.cur.execute("DELETE FROM Participations")
        self.con.commit()

    def add_pot_data(
        self,
        pot_id: int,
        volume: int,
        started: bool,
        finished: bool,
        remaining_blocks: int,
    ) -> None:
        self.cur.execute(
            "REPLACE INTO Pots VALUES(%s, %s, %s, %s, %s)",
            (pot_id, volume, started, finished, remaining_blocks),
        )
        self.con.commit()

    def add_partisipant_data(self, participant: str, pot_id: int, volume: int) -> None:
        self.cur.execute(
            "INSERT INTO  PartisipantsVALUES",
            (pot_id, volume, started, finished, remaining_blocks),
        )
        self.con.commit()
