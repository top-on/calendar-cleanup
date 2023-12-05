"""Purge old events from a calendar."""

# %%
# importat and config

from datetime import date, datetime, timedelta

import typer
from ical.calendar import Calendar
from ical.calendar_stream import CalendarParseError, IcsCalendarStream

from calendar_cleanup.io.auth import (
    create_webdav_client,
    request_credentials,
)
from calendar_cleanup.io.load import list_ics_filepaths, load_ics_content

# %%
app = typer.Typer(add_completion=False)


@app.command()
def clean(days: int = 30) -> None:
    """Purge old events from a WebDAV calendar.

    Args:\n
        days: Number of days into past from which on to delete events. Defaults to 30.
    """
    # %%
    # events older than this will be deleted
    purge_before: date = datetime.now().date() - timedelta(days=days)

    credentials = request_credentials()
    client = create_webdav_client(credentials)

    ics_filepaths = list_ics_filepaths(client=client)
    file_contents = load_ics_content(
        ics_filepaths=ics_filepaths,
        client=client,
    )

    # %%
    # parse ICS content to Calendar objects

    print("\nParsing ICS files...")
    filenames_calendars: list[tuple[str, Calendar]] = []
    for filepath, file_content in zip(ics_filepaths, file_contents):
        try:
            print(f"Parsing ICS file '{filepath}'...")
            calendar = IcsCalendarStream.calendar_from_ics(file_content)
            filenames_calendars.append((filepath, calendar))
        except CalendarParseError as e:
            print(f"Failed to parse file {filepath}: {e}. Next.")
            continue

    print(f"Parsed {len(filenames_calendars)} ICS files.")

    # %%
    # check which files can be deleted

    print("\nChecking which files can be deleted...")
    filenames_summaries_dates_to_delete: list[tuple[str, str, date]] = []
    for filepath, calendar in filenames_calendars:
        # skip if file is a todo
        has_event = len(calendar.events) > 0
        has_todos = len(calendar.todos) > 0
        if not has_event and has_todos:
            print(f"File '{filepath}' is a TODO file. Next.")
            continue

        # skip if file contains more than one event
        is_single_event = len(calendar.events) == 1
        if not is_single_event:
            print(f"File '{filepath}' does not contain a single event. Next.")
            continue

        event = calendar.events[0]

        # extract timezone-aware start datetime
        if type(event.dtstart) is datetime:
            event_date = event.dtstart.date()
        elif type(event.dtstart) is date:
            event_date = event.dtstart
        else:
            print(f"Event '{event.summary}' has no start date. Next.")
            continue

        # skip if event is repeating
        is_repeating = event.rrule is not None
        if is_repeating:
            print(f"Event '{event.summary}' is repeating. Next.")
            continue

        is_old_enough = event_date < purge_before
        if not is_old_enough:
            print(f"Event '{event.summary}' is not old enough ({event_date}). Next.")
            continue

        # if we get here, we can ask the user if the event should be deleted
        filenames_summaries_dates_to_delete.append(
            (filepath, event.summary, event_date)
        )

    print(
        f"\nFound {len(filenames_summaries_dates_to_delete)} events okay for deletion."
    )

    # %%
    # ask user if event should be deleted

    filenames_summaries_dates_sorted = sorted(
        filenames_summaries_dates_to_delete, key=lambda x: x[2]
    )

    if len(filenames_summaries_dates_sorted) == 0:
        print("\nNo events to delete. Exiting.")
        exit(0)

    # print out all events that can be deleted
    print("\nEvents that can be deleted:")
    for _, summary, event_date in filenames_summaries_dates_sorted:
        print(f"- {str(event_date)}: {summary}")

    # %%
    if input("\nDelete listed events? [y/N] ").lower() == "y":
        print("Deletion confirmed. Deleting events...")
    else:
        print("Deletion not confirmed. Exiting.")
        exit(0)

    # %%
    # bulk delete files

    for filepath, summary, _ in filenames_summaries_dates_sorted:  # type: ignore
        print(f"Deleting event: '{summary}' ...")
        client.remove(filepath)

    print("Deletion completed.")


# %%

if __name__ == "__main__":
    app()
