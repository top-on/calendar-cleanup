# Calendar Cleanup

CLI utility to unclutter WebDAV calendars by deleting old entries.

```bash
    Usage: calendar-cleanup [OPTIONS]

    CLI utility to unclutter WebDAV calendars by deleting old entries.

    The CLI tools proposes which old entries to remove. If the user approves,
    the events get deleted.

    Options:
    --days INTEGER  Number of days into past from which on to delete events.
                    [default: 30]
    --help          Show this message and exit.
```

# Roadmap

- [ ] introduce logging at varing verbosity levels, replacing print statements
