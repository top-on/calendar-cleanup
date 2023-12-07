"""Functions for filtering events to delete."""

from datetime import date, datetime, timedelta

from ical.calendar import Calendar

from calendar_cleanup.schema import CalendarEvent


# TODO: include into pipeline
def transform_to_calendar_event(
    filepath=str,
    calendar=Calendar,
) -> CalendarEvent | ValueError:
    """
    Transform a filename and Calendar to a CalendarEvent.

    Args:
        filepath: file location on WebDAV storage.
        calendar: corresponding Calendar object.
    Returns:
        CalendarEvent object with information needed for filtering and deletion.
        If event cannot be transformed, a ValueError is *retured*.
    """
    # verify that record is no todo
    if len(calendar.todos) > 0:
        return ValueError("Is a TODO file.")

    # verify that .ical file contains a single event
    if len(calendar.events) != 1:
        return ValueError("Is not single event.")

    # verify that event is not repeating
    event = calendar.events[0]
    if event.rrule is not None:
        return ValueError("Is repeating.")

    # extract start date
    if type(event.dtstart) is datetime:
        event_date = event.dtstart.date()
    elif type(event.dtstart) is date:
        event_date = event.dtstart
    else:
        return ValueError("No start date.")

    # make transformation
    calendar_event = CalendarEvent(
        filepath=filepath,
        summary=event.summary,
        event_date=event_date,
    )
    return calendar_event


def filter_events_to_clean(
    filenames_calendars: list[tuple[str, Calendar]],
    today: date,
    days: int,
) -> list[tuple[str, str, date]]:
    """Identify events that can be marked for deletion.

    Args:
        filenames_calendars: tuples with filepath and corresponding Calendar object.
        today: The current date.
        days: Number of days before today for an event to be old enough for deletion.
    Returns:
        Events marked for deletion, identified by their filepath, event summary, date.
    """
    # events older than this will be marked for deletion
    purge_before: date = today - timedelta(days=days)

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

    print(f"\nFound {len(filenames_summaries_dates_to_delete)} events for deletion.")
    return filenames_summaries_dates_to_delete
