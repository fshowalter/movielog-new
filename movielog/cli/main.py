from movielog import exporter, imdb_s3_orchestrator
from movielog.cli import (
    add_viewing,
    confirm,
    manage_watchlist,
    radio_list,
    reload_viewings,
    reload_reviews,
)
from movielog.logger import logger


@logger.catch
def prompt() -> None:
    options = [
        (add_viewing.prompt, "<cyan>Add Viewing</cyan>"),
        (manage_watchlist.prompt, "<cyan>Manage Watchlist</cyan>"),
        (update_imdb_s3_data, "<cyan>Update IMDb data</cyan>"),
        (reload_viewings.prompt, "<cyan>Reload Viewings Table</cyan>"),
        (reload_reviews.prompt, "<cyan>Reload Reviews Table</cyan>"),
        (export, "<cyan>Export Data</cyan>"),
        (None, "Exit"),
    ]

    option_function = radio_list.prompt(title="Movie DB options:", options=options,)
    if option_function:
        option_function()
        prompt()


def export() -> None:
    prompt_text = "<cyan>Export review, viewing, watchlist, and stats data?</cyan>"
    if confirm.prompt(prompt_text):
        exporter.export()


def update_imdb_s3_data() -> None:
    if confirm.prompt("<cyan>Download and update IMDb data?</cyan>"):
        imdb_s3_orchestrator.orchestrate_update()
