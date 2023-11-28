"""Purge old events from a calendar."""

# %%
# importat and config

from datetime import datetime, timedelta
from getpass import getpass

import pytz
from ical.calendar_stream import CalendarParseError, IcsCalendarStream
from webdav4.client import Client, HTTPError, ResourceNotFound

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

filenames = [file["name"] for file in files]

# %%
# load files into memory

print("\nDownloading WebDAV files...")

file_contents = []
for filename, file in zip(filenames, files):
    print(f"Downloading file '{filename}'...")
    with client.open(filename, "r") as f:
        file_contents.append(f.read())

print(f"Downloaded {len(file_contents)} WebDAV files.")


# %%
for filename, file_content in zip(filenames, file_contents):
    # parse file content
    try:
        print(f"\nParsing ICS file '{filename}'...")
        calendar = IcsCalendarStream.calendar_from_ics(file_content)
    except ResourceNotFound:
        print(f"File {filename} not found on server.")
        continue
    except CalendarParseError as e:
        print(f"Failed to parse file {filename}: {e}. Next.")
        continue

    # skip if file is a todo
    has_event = len(calendar.events) > 0
    has_todos = len(calendar.todos) > 0
    if not has_event and has_todos:
        print(f"File {filename} is a TODO file. Next.")
        continue

    # skip if file contains more than one event
    is_single_event = len(calendar.events) == 1
    if not is_single_event:
        print(f"File {filename} does not contain a single event. Next.")
        continue

    event = calendar.events[0]
    summary = f"{event.dtstart}: {event.summary}"

    # skip if event is repeating
    is_repeating = event.rrule is not None
    if is_repeating:
        print(f"Event '{summary}' is repeating. Next.")
        continue

    # skip if event is not old enough
    event_start = event.dtstart
    # make sure we have a datetime object
    event_start_dt = datetime.combine(event_start, datetime.min.time())
    # make sure we have a timezone aware datetime object
    event_start_dt_berlin = event_start_dt.astimezone(pytz.timezone("Europe/Berlin"))
    is_old = event_start_dt_berlin < PURGE_BEFORE
    if not is_old:
        print(f"Event '{summary}' is not old enough. Next.")
        continue

    # ask user if event should be deleted
    if input(f"Delete event '{summary}'? [y/N] ").lower() == "y":
        print("Deleting file...")
        client.remove(filename)
    else:
        print("Not deleting event. Next.")

    # %%
