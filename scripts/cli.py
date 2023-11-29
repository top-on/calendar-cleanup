"""Purge old events from a calendar."""

# %%
# importat and config

from datetime import date, datetime, timedelta
from getpass import getpass

import typer
from ical.calendar import Calendar
from ical.calendar_stream import CalendarParseError, IcsCalendarStream
from webdav4.client import Client, HTTPError

# %%
app = typer.Typer(add_completion=False)


@app.command()
def clean(days: int = 30):
    """Purge old events from a WebDAV calendar.

    Args:\n
        days: Number of days into past from which on to delete events. Defaults to 30.
    """
    # %%
    # events older than this will be deleted
    purge_before: date = datetime.now().date() - timedelta(days=days)

    # %%
    # request credentials

    print("Please enter the credentials for your WebDAV calendar.")
    username = input("username: ")
    password = getpass("password: ")

    # read input for url with a default
    default_url = f"https://posteo.de:8443/calendars/{username}/default"
    url = input(f"Calendar URL [{default_url}]: ") or default_url

    # %%
    # create webdav client

    client = Client(base_url=url, auth=(username, password))

    print("Verifying authentication...")
    try:
        client.exists(".")  # verify authentication
    except HTTPError as e:
        print(f"Authentication with WebDAV server failed: '{e}'. Exiting.")
        exit(1)
    print("Authentication successful.")

    # %%
    # list files

    print("\nListing WebDAV files...")
    files = client.ls(".")
    print(f"Found {len(files)} WebDAV files.")

    filenames: list[str] = [file["name"] for file in files]

    # %%
    # load files into memory

    print("\nReading WebDAV files' content...")

    file_contents: list[str] = []
    for filename, file in zip(filenames, files):
        print(f"Reading content from '{filename}'...")
        with client.open(filename, "r") as f:
            file_contents.append(f.read())

    print(f"Downloaded {len(file_contents)} WebDAV files.")

    # %%
    # parse ICS content to Calendar objects

    print("\nParsing ICS files...")
    filenames_calendars: list[tuple[str, Calendar]] = []
    for filename, file_content in zip(filenames, file_contents):
        try:
            print(f"Parsing ICS file '{filename}'...")
            calendar = IcsCalendarStream.calendar_from_ics(file_content)
            filenames_calendars.append((filename, calendar))
        except CalendarParseError as e:
            print(f"Failed to parse file {filename}: {e}. Next.")
            continue

    print(f"Parsed {len(filenames_calendars)} ICS files.")

    # %%
    # check which files can be deleted

    print("\nChecking which files can be deleted...")
    filenames_summaries_dates_to_delete: list[tuple[str, str, date]] = []
    for filename, calendar in filenames_calendars:
        # skip if file is a todo
        has_event = len(calendar.events) > 0
        has_todos = len(calendar.todos) > 0
        if not has_event and has_todos:
            print(f"File '{filename}' is a TODO file. Next.")
            continue

        # skip if file contains more than one event
        is_single_event = len(calendar.events) == 1
        if not is_single_event:
            print(f"File '{filename}' does not contain a single event. Next.")
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
            (filename, event.summary, event_date)
        )

    print(
        f"\nFound {len(filenames_summaries_dates_to_delete)} events that can be deleted."
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

    for filename, summary, _ in filenames_summaries_dates_sorted:  # type: ignore
        print(f"Deleting event: '{summary}' ...")
        client.remove(filename)

    print("Deletion completed.")


# %%

if __name__ == "__main__":
    app()
