# Calendar Cleanup

CLI utility to unclutter WebDAV calendars by deleting old entries.

## Installation

```bash
pip install calendar-cleanup
```

## Usage example

```bash
$ calendar-cleanup

Please enter the credentials for your WebDAV calendar.

username: john.doe
password:
Calendar URL:

Verifying authentication...
Authentication successful.

Reading WebDAV files content...
Loaded content from 25 WebDAV files.

Parsing ICS content...
Successfully parsed 22 of 25 ICS files.

Found 2 events for deletion.

Events that can be deleted:
- 2023-11-14: Lorem ipsum
- 2023-11-16: Lorem ipsum follow-up

Delete listed events? [y/N]
Deletion not confirmed. Exiting.
```

## CLI documentation

```
Usage: calendar-cleanup [OPTIONS]

CLI utility to unclutter WebDAV calendars by deleting old entries.

The CLI tools proposes which old entries to remove. If the user approves,
the events get deleted.

Options:
-d, --days INTEGER  Number of days into past from which on to delete events.
                    [default: 30]
-v, --verbose       Enable detailed output.
--help              Show this message and exit.
```
