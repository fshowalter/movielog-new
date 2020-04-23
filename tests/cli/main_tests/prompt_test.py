import pytest
from pytest_mock import MockFixture

from movielog.cli import main
from tests.cli.keys import ControlD, Down, End, Enter, Up
from tests.cli.typehints import PosixPipeInput


@pytest.fixture(autouse=True)
def mock_add_viewing(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.main.add_viewing.prompt")


@pytest.fixture(autouse=True)
def mock_manage_watchlist(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.main.manage_watchlist.prompt")


@pytest.fixture(autouse=True)
def mock_update_viewings(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.main.update_viewings.prompt")


@pytest.fixture(autouse=True)
def mock_imdb_s3_orchestrator_orchestrate_update(mocker: MockFixture) -> MockFixture:
    return mocker.patch("movielog.cli.main.imdb_s3_orchestrator.orchestrate_update")


def test_calls_add_viewing(
    mock_input: PosixPipeInput, mock_add_viewing: MockFixture
) -> None:
    mock_input.send_text("".join([Enter, ControlD]))
    main.prompt()

    mock_add_viewing.assert_called_once()


def test_calls_manage_watchlist(
    mock_input: PosixPipeInput, mock_manage_watchlist: MockFixture
) -> None:
    mock_input.send_text("".join([Down, Enter, End, Enter]))
    main.prompt()

    mock_manage_watchlist.assert_called_once()


def test_calls_update_viewings(
    mock_input: PosixPipeInput, mock_update_viewings: MockFixture
) -> None:
    mock_input.send_text("".join([Up, Up, Enter, End, Enter]))
    main.prompt()

    mock_update_viewings.assert_called_once()


def test_calls_imdb_s3_orchestrator_update(
    mock_input: PosixPipeInput,
    mock_imdb_s3_orchestrator_orchestrate_update: MockFixture,
) -> None:
    mock_input.send_text(f"{Down}{Down}{Enter}y{Up}{Enter}")
    main.prompt()

    mock_imdb_s3_orchestrator_orchestrate_update.assert_called_once()


def test_can_confirm_imdb_s3_orchestrator_update(
    mock_input: PosixPipeInput,
    mock_imdb_s3_orchestrator_orchestrate_update: MockFixture,
) -> None:
    mock_input.send_text(f"{Down}{Down}{Enter}n{Up}{Enter}")
    main.prompt()

    mock_imdb_s3_orchestrator_orchestrate_update.assert_not_called()
