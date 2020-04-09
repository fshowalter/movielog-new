from dataclasses import dataclass
from typing import Dict, List

from movielog import db
from movielog.cli import query_formatter


@dataclass
class Result(object):
    __slots__ = (
        "imdb_id",
        "name",
        "known_for_title_ids",
        "known_for_titles",
    )
    imdb_id: str
    name: str
    known_for_title_ids: str
    known_for_titles: List[str]

    @classmethod
    def from_query_result(cls, row: Dict[str, str]) -> "Result":
        return cls(
            imdb_id=row["imdb_id"],
            name=row["full_name"],
            known_for_title_ids=row["known_for_title_ids"],
            known_for_titles=[],
        )


def search_directors_by_name(name: str, limit: int = 10) -> List[Result]:
    query = query_formatter.add_wildcards(name)

    full_query = """
        SELECT distinct(people.imdb_id), full_name, known_for_title_ids FROM people
        INNER JOIN directing_credits ON people.imdb_id = directing_credits.person_imdb_id
        WHERE full_name LIKE "{0}" ORDER BY full_name LIMIT {1};
        """.format(  # noqa: S608
        query, limit
    )

    return execute_search(full_query)


def search_performers_by_name(name: str, limit: int = 10) -> List[Result]:
    query = query_formatter.add_wildcards(name)

    full_query = """
        SELECT distinct(people.imdb_id), full_name, known_for_title_ids FROM people
        WHERE full_name LIKE "{0}" ORDER BY full_name LIMIT {1};
        """.format(  # noqa: S608
        query, limit
    )

    return execute_search(full_query)


def search_writers_by_name(name: str, limit: int = 10) -> List[Result]:
    query = query_formatter.add_wildcards(name)

    full_query = """
        SELECT distinct(people.imdb_id), full_name, known_for_title_ids FROM people
        INNER JOIN writing_credits ON people.imdb_id = writing_credits.person_imdb_id
        WHERE full_name LIKE "{0}" ORDER BY full_name LIMIT {1};
        """.format(  # noqa: S608
        query, limit
    )

    return execute_search(full_query)


def execute_search(query: str) -> List[Result]:
    with db.connect() as connection:
        search_results = fetch_results(connection, query)
        resolve_known_for_titles(connection, search_results)

    return search_results


def fetch_results(connection: db.Connection, query: str) -> List[Result]:
    cursor = connection.cursor()
    rows = cursor.execute(query).fetchall()

    search_results: List[Result] = []

    for row in rows:
        search_result = Result.from_query_result(row)
        search_results.append(search_result)

    return search_results


def resolve_known_for_titles(
    connection: db.Connection, search_results: List[Result]
) -> None:
    title_cache = build_title_cache(
        connection=connection, search_results=search_results
    )

    for search_result in search_results:
        for title_id in search_result.known_for_title_ids.split(","):
            title = title_cache.get(title_id, None)
            if title:
                search_result.known_for_titles.append(title)


def build_title_cache(
    connection: db.Connection, search_results: List[Result]
) -> Dict[str, str]:
    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT imdb_id, title FROM movies where imdb_id IN ({0});
        """.format(  # noqa: S608
            format_known_for_title_ids(search_results)
        ),
    ).fetchall()

    return {row["imdb_id"]: row["title"] for row in rows}


def format_known_for_title_ids(search_results: List[Result]) -> str:
    title_ids: List[str] = []

    for search_result in search_results:
        title_ids.extend(search_result.known_for_title_ids.split(","))

    return ",".join('"{0}"'.format(title_id) for title_id in title_ids)
