"""Purge old events from a calendar."""

# %%
# importat and config

from datetime import datetime, timedelta
from getpass import getpass

import pytz
from ical.calendar_stream import CalendarParseError, IcsCalendarStream
from webdav4.client import Client, ResourceNotFound

# events older than this will be deleted
PURGE_BEFORE = datetime.now(pytz.timezone("Europe/Berlin")) - timedelta(days=30)

# %%
# request credentials

user = input("User: ")
password = getpass("Password: ")

# read input for url with a default
default_url = f"https://posteo.de:8443/calendars/{user}/default"
url = input(f"Calendar URL [{default_url}]: ") or default_url

# %%
# create client

client = Client(base_url=url, auth=(user, password))
client.exists(".")  # verify authentication

# %%
# list files

print("\nListing calendar files...")
files = client.ls(".")
print(f"Found {len(files)} event files.")

# %%
for file in files:
    filename = file["name"]

    # load and parse file
    try:
        print(f"\nLoading file {filename}...")
        with client.open(filename, "r") as f:
            calendar = IcsCalendarStream.calendar_from_ics(f.read())
    except ResourceNotFound:
        print(f"File {filename} not found on server.")
        continue
    except CalendarParseError as e:
        print(f"Failed to parse file {filename}: {e}. Next.")
        continue

    # check if file is a todo
    has_event = len(calendar.events) > 0
    has_todos = len(calendar.todos) > 0
    if not has_event and has_todos:
        print(f"File {filename} is a TODO file. Next.")
        continue

    is_single_event = len(calendar.events) == 1
    if not is_single_event:
        print(f"File {filename} does not contain a single event. Next.")
        continue

    event = calendar.events[0]
    summary = f"{event.dtstart}: {event.summary}"

    event_start = event.dtstart
    # make sure we have a datetime object
    event_start_dt = datetime.combine(event_start, datetime.min.time())
    # make sure we have a timezone aware datetime object
    event_start_dt_berlin = event_start_dt.astimezone(pytz.timezone("Europe/Berlin"))

    is_repeating = event.rrule is not None
    is_old = event_start_dt_berlin < PURGE_BEFORE

    if not is_old:
        print(f"Event '{summary}' is not old enough. Next.")
        continue
    if is_repeating:
        print(f"Event '{summary}' is repeating. Next.")
        continue

    # delete file
    if input(f"Delete event '{summary}'? [y/N] ").lower() == "y":
        print("Deleting file...")
        client.remove(filename)
    else:
        print("Not deleting event. Next.")

    # %%
