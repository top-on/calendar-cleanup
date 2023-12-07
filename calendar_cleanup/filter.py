"""Functions for filtering events to delete."""

from datetime import date, datetime, timedelta

from ical.calendar import Calendar

from calendar_cleanup.schema import CalendarEvent


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
) -> list[CalendarEvent]:
    """Identify events that can be marked for deletion.

    Args:
        filenames_calendars: tuples with filepath and corresponding Calendar object.
        today: The current date.
        days: Number of days before today for an event to be old enough for deletion.
    Returns:
        CalendarEvents marked for deletion.
    """
    # transform filenames and calendars to CalendarEvent objects
    calendar_events: list[CalendarEvent | ValueError] = [
        transform_to_calendar_event(filepath=filepath, calendar=calendar)
        for filepath, calendar in filenames_calendars
    ]

    # filter out value errors from transformation
    calendar_events_valid: list[CalendarEvent] = [
        calendar_event
        for calendar_event in calendar_events
        if isinstance(calendar_event, CalendarEvent)
    ]

    # filter out events that are not old enough
    calendar_events_old_enough: list[CalendarEvent] = [
        calendar_event
        for calendar_event in calendar_events_valid
        if calendar_event.event_date < today - timedelta(days=days)
    ]

    print(f"\nFound {len(calendar_events_old_enough)} events for deletion.")
    return calendar_events_old_enough
