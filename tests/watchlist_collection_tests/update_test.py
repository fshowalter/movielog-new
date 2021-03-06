from pytest_mock import MockerFixture

from movielog import watchlist_collection


def test_saves_collection(mocker: MockerFixture) -> None:
    collection = watchlist_collection.Collection(name="Test Collection")
    save_mock = mocker.patch.object(collection, "save")

    watchlist_collection.update(collection)

    save_mock.assert_called_once()
