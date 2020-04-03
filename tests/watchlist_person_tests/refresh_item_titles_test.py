from typing import List, Type, Union

import pytest
from pytest_mock import MockFixture

from movielog import imdb_http
from movielog.watchlist_file import Title
from movielog.watchlist_person import Director, Performer, Writer


@pytest.fixture
def credits_for_person() -> List[imdb_http.CreditForPerson]:
    return [
        imdb_http.CreditForPerson(
            imdb_id="tt0053125",
            title="North by Northwest",
            year="1959",
            notes="",
            in_production="",
        ),
        imdb_http.CreditForPerson(
            imdb_id="tt9999999",
            title="North by Northwest 2",
            year="2025",
            notes="based on",
            in_production="",
        ),
        imdb_http.CreditForPerson(
            imdb_id="tt0017075",
            title="The Lodger: A Story of the London Fog",
            year="1927",
            notes="",
            in_production="",
        ),
    ]


@pytest.fixture(autouse=True)
def credits_for_person_mock(
    mocker: MockFixture, credits_for_person: List[imdb_http.CreditForPerson]
) -> MockFixture:
    return mocker.patch(
        "movielog.imdb_http.credits_for_person", return_value=credits_for_person
    )


@pytest.mark.parametrize(
    "class_type", [Director, Performer, Writer],
)
def test_refreshes_titles_from_imdb(
    mocker: MockFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    credits_for_person: List[imdb_http.CreditForPerson],
    credits_for_person_mock: MockFixture,
) -> None:
    expected = [
        Title(imdb_id="tt0053125", title="North by Northwest", year="1959", notes=""),
        Title(
            imdb_id="tt9999999",
            title="North by Northwest 2",
            year="2025",
            notes="based on",
        ),
        Title(
            imdb_id="tt0017075",
            title="The Lodger: A Story of the London Fog",
            year="1927",
            notes="",
        ),
    ]

    for credit_for_person in credits_for_person:
        mocker.patch.object(credit_for_person, "is_silent_film", return_value=False)

    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")

    valid_movie_ids = set(["tt0053125", "tt9999999", "tt0017075"])

    mocker.patch(
        "movielog.watchlist_person.movies.title_ids", return_value=valid_movie_ids
    )

    save_mock = mocker.patch.object(person, "save")

    person.refresh_item_titles()

    assert person.titles == expected

    save_mock.assert_called_once()


@pytest.mark.parametrize(
    "class_type", [Director, Performer, Writer],
)
def test_skips_invalid_titles(
    mocker: MockFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    credits_for_person: List[imdb_http.CreditForPerson],
    credits_for_person_mock: MockFixture,
) -> None:
    expected = [
        Title(imdb_id="tt0053125", title="North by Northwest", year="1959", notes=""),
        Title(
            imdb_id="tt0017075",
            title="The Lodger: A Story of the London Fog",
            year="1927",
            notes="",
        ),
    ]

    for credit_for_person in credits_for_person:
        mocker.patch.object(credit_for_person, "is_silent_film", return_value=False)

    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")

    valid_movie_ids = set(["tt0053125", "tt0017075"])

    mocker.patch(
        "movielog.watchlist_person.movies.title_ids", return_value=valid_movie_ids
    )

    save_mock = mocker.patch.object(person, "save")

    person.refresh_item_titles()

    assert person.titles == expected

    save_mock.assert_called_once()


@pytest.mark.parametrize(
    "class_type", [Director, Performer, Writer],
)
def test_skips_silent_movies(
    mocker: MockFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    credits_for_person: List[imdb_http.CreditForPerson],
    credits_for_person_mock: MockFixture,
) -> None:
    expected = [
        Title(imdb_id="tt0053125", title="North by Northwest", year="1959", notes=""),
        Title(
            imdb_id="tt9999999",
            title="North by Northwest 2",
            year="2025",
            notes="based on",
        ),
    ]

    mocker.patch.object(credits_for_person[0], "is_silent_film", return_value=False)
    mocker.patch.object(credits_for_person[1], "is_silent_film", return_value=False)
    mocker.patch.object(credits_for_person[2], "is_silent_film", return_value=True)

    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")

    valid_movie_ids = set(["tt0053125", "tt9999999", "tt0017075"])

    mocker.patch(
        "movielog.watchlist_person.movies.title_ids", return_value=valid_movie_ids
    )

    save_mock = mocker.patch.object(person, "save")

    person.refresh_item_titles()

    assert person.titles == expected

    save_mock.assert_called_once()


@pytest.mark.parametrize(
    "class_type", [Director, Performer, Writer],
)
def test_skips_in_production_titles(
    mocker: MockFixture,
    class_type: Type[Union[Performer, Director, Writer]],
    credits_for_person: List[imdb_http.CreditForPerson],
    credits_for_person_mock: MockFixture,
) -> None:
    expected = [
        Title(imdb_id="tt0053125", title="North by Northwest", year="1959", notes=""),
        Title(
            imdb_id="tt0017075",
            title="The Lodger: A Story of the London Fog",
            year="1927",
            notes="",
        ),
    ]

    credits_for_person[1].in_production = "in-development"

    for credit_for_person in credits_for_person:
        mocker.patch.object(credit_for_person, "is_silent_film", return_value=False)

    person = class_type(file_path=None, name="Alfred Hitchcock", imdb_id="nm0000033")

    valid_movie_ids = set(["tt0053125", "tt9999999", "tt0017075"])

    mocker.patch(
        "movielog.watchlist_person.movies.title_ids", return_value=valid_movie_ids
    )

    save_mock = mocker.patch.object(person, "save")

    person.refresh_item_titles()

    assert person.titles == expected

    save_mock.assert_called_once()