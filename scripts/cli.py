"""Purge old events from a calendar."""

from datetime import date

import typer

from calendar_cleanup.filter import filter_events_to_clean
from calendar_cleanup.io.auth import (
    create_webdav_client,
    request_credentials,
)
from calendar_cleanup.io.delete import confirm_and_delete_events, sort_and_print_events
from calendar_cleanup.io.load import (
    list_ics_filepaths,
    load_ics_content,
    parse_ics_content,
)

app = typer.Typer(add_completion=False)


@app.command()
def clean(days: int = 30) -> None:
    """Purge old events from a WebDAV calendar.

    Args:\n
        days: Number of days into past from which on to delete events. Defaults to 30.
    """
    # authenticate with WebDAV server
    credentials = request_credentials()
    client = create_webdav_client(credentials)

    # list, load, and parse calendar files
    ics_filepaths = list_ics_filepaths(client=client)
    file_contents = load_ics_content(
        ics_filepaths=ics_filepaths,
        client=client,
    )
    filenames_calendars = parse_ics_content(
        ics_filepaths=ics_filepaths,
        file_contents=file_contents,
    )

    # identify Calendar Events that can be deleted. if there are none, exit.
    calendar_events_to_delete = filter_events_to_clean(
        filenames_calendars=filenames_calendars,
        today=date.today(),
        days=days,
    )
    if len(calendar_events_to_delete) == 0:
        print("\nNo events to delete. Exiting.")
        exit(code=0)

    # check with user if Calendar Events can be deleted, then delete them
    calendar_events_sorted = sort_and_print_events(
        calendar_events=calendar_events_to_delete
    )
    confirm_and_delete_events(
        calendar_events=calendar_events_sorted,
        client=client,
    )


if __name__ == "__main__":
    app()
