import os
from typing import Set
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from movielog import crew_credits


@pytest.fixture(autouse=True)
def imdb_s3_download_mock(mocker: MockerFixture, gzip_file: MagicMock) -> MagicMock:
    file_path = gzip_file(
        os.path.join(os.path.dirname(__file__), "crew_credits_test_data.tsv")
    )

    return mocker.patch(
        "movielog.crew_credits.imdb_s3_downloader.download", return_value=file_path
    )


@pytest.fixture(autouse=True)
def movie_ids_mock(mocker: MockerFixture) -> MagicMock:
    valid_ids: Set[str] = set(["tt0000001", "tt0053221", "tt0089175"])
    return mocker.patch(
        "movielog.crew_credits.movies.title_ids", return_value=valid_ids
    )


@pytest.fixture(autouse=True)
def remove_movies_not_in_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("movielog.crew_credits.movies.remove_movies_not_in")


def test_inserts_people_from_downloaded_s3_file(sql_query: MagicMock) -> None:
    expected_directors = [
        ("tt0053221", "nm0001328", 0, None),
        ("tt0089175", "nm0276169", 0, None),
        ("tt0000001", "nm0005690", 0, None),
    ]

    expected_writers = [
        ("tt0053221", "nm0299154", 0, None),
        ("tt0053221", "nm0102824", 1, None),
        ("tt0053221", "nm0564800", 2, None),
        ("tt0089175", "nm0276169", 0, None),
    ]

    crew_credits.update()

    assert sql_query("SELECT * FROM 'directing_credits';") == expected_directors
    assert sql_query("SELECT * FROM 'writing_credits';") == expected_writers


def test_calls_remove_movies_with_no_directors(
    remove_movies_not_in_mock: MagicMock,
) -> None:
    crew_credits.update()

    remove_movies_not_in_mock.assert_called_with(
        ["tt0053221", "tt0089175", "tt0000001"],
    )
