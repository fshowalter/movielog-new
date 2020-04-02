from dataclasses import asdict, dataclass
from typing import List, Optional, Tuple

from movielog import db, humanize, imdb_s3_downloader, imdb_s3_extractor, movies
from movielog.logger import logger

FILE_NAME = "title.crew.tsv.gz"
DIRECTING_CREDITS_TABLE_NAME = "directing_credits"
WRITING_CREDITS_TABLE_NAME = "writing_credits"


@dataclass
class CrewCredit(object):
    __slots__ = ("movie_imdb_id", "person_imdb_id", "sequence")
    movie_imdb_id: str
    person_imdb_id: str
    sequence: str


class CreditsTable(db.Table):
    table_name: str
    recreate_ddl = """
        DROP TABLE IF EXISTS "{0}";
        CREATE TABLE "{0}" (
            "movie_imdb_id" varchar(255) NOT NULL
                REFERENCES movies(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "person_imdb_id" varchar(255) NOT NULL
                REFERENCES people(imdb_id) DEFERRABLE INITIALLY DEFERRED,
            "sequence" INT NOT NULL,
            PRIMARY KEY (movie_imdb_id, person_imdb_id));
        """

    @classmethod
    def insert_credits(cls, credit_items: List[CrewCredit]) -> None:
        ddl = """
        INSERT INTO {0} (movie_imdb_id, person_imdb_id, sequence)
        VALUES(:movie_imdb_id, :person_imdb_id, :sequence);
        """.format(
            cls.table_name
        )

        parameter_seq = [asdict(credit) for credit in credit_items]

        cls.insert(ddl=ddl, parameter_seq=parameter_seq)
        cls.add_index("person_imdb_id")
        cls.validate(credit_items)


class DirectingCreditsTable(CreditsTable):
    table_name = DIRECTING_CREDITS_TABLE_NAME


class WritingCreditsTable(CreditsTable):
    table_name = DIRECTING_CREDITS_TABLE_NAME


def update() -> None:
    logger.log(
        "==== Begin updating {} and {}...",
        DIRECTING_CREDITS_TABLE_NAME,
        WRITING_CREDITS_TABLE_NAME,
    )

    downloaded_file_path = imdb_s3_downloader.download(FILE_NAME)

    for _ in imdb_s3_extractor.checkpoint(downloaded_file_path):  # noqa: WPS122
        directing_credits, writing_credits = _extract_credits(downloaded_file_path)
        DirectingCreditsTable.recreate()
        DirectingCreditsTable.insert_credits(directing_credits)
        WritingCreditsTable.recreate()
        WritingCreditsTable.insert_credits(writing_credits)


def _extract_credits(
    downloaded_file_path: str,
) -> Tuple[List[CrewCredit], List[CrewCredit]]:
    title_ids = movies.title_ids()
    directing_credits: List[CrewCredit] = []
    writing_credits: List[CrewCredit] = []

    for fields in imdb_s3_extractor.extract(downloaded_file_path):
        title_id = fields[0]
        if title_id in title_ids:
            directing_credits.extend(_fields_to_credits(fields, 1))
            writing_credits.extend(_fields_to_credits(fields, 2))

    logger.log(
        "Extracted {} {}.",
        humanize.intcomma(len(directing_credits)),
        DIRECTING_CREDITS_TABLE_NAME,
    )
    logger.log(
        "Extracted {} {}.",
        humanize.intcomma(len(writing_credits)),
        WRITING_CREDITS_TABLE_NAME,
    )

    return (directing_credits, writing_credits)


def _fields_to_credits(
    fields: List[Optional[str]], credit_index: int
) -> List[CrewCredit]:
    crew_credits: List[CrewCredit] = []

    if fields[credit_index] is None:
        return crew_credits

    for sequence, person_imdb_id in enumerate(str(fields[credit_index]).split(",")):
        crew_credits.append(
            CrewCredit(
                movie_imdb_id=str(fields[0]),
                person_imdb_id=person_imdb_id,
                sequence=str(sequence),
            )
        )

    return crew_credits