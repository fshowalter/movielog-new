from typing import Any

from prompt_toolkit.formatted_text import HTML

from movie_db.cli import (
    add_viewing,
    manage_watchlist,
    update_imdb_data,
    update_viewings,
)
from movie_db.logger import logger
from movielog.cli.internal import radio_list


@logger.catch
def prompt(args=None) -> Any:
    options = radio_list.CallableOptions(
        [
            (add_viewing.prompt, HTML("<cyan>Add Viewing</cyan>")),
            (manage_watchlist.prompt, HTML("<cyan>Manage Watchlist</cyan>")),
            (update_imdb_data.prompt, HTML("<cyan>Update IMDb data</cyan>")),
            (update_viewings.prompt, HTML("<cyan>Update Viewings</cyan>")),
            (None, "Exit"),
        ]
    )

    option_function = radio_list.prompt(title="Movie DB options:", options=options,)

    if option_function:
        option_function()
        prompt()