"""Test filtering logic."""

from datetime import datetime, timedelta

import pytest
from ical.calendar import Calendar, Event, Todo
from ical.types import Frequency, Recur

from calendar_cleanup.filter import filter_events_to_clean, transform_to_calendar_event
from calendar_cleanup.schema import CalendarEvent


def test_filter_events_to_clean():
    """Test filtering logic."""

    # test data
    filename = "test.ics"
    event_date = datetime(2022, 8, 31).date()
    event = Event(
        summary="Test event",
        dtstart=event_date,
        dtend=event_date + timedelta(hours=1),
    )
    calendar = Calendar(events=[event])
    filenames_calendars = [(filename, calendar)]

    # run
    result = filter_events_to_clean(
        filenames_calendars=filenames_calendars,
        today=datetime.now().date(),
        days=30,
    )

    # assert
    assert len(result) == 1
    assert result[0][0] == filename
    assert result[0][1] == event.summary
    assert result[0][2] == event_date


@pytest.mark.parametrize(
    "calendar, expected",
    [
        (
            Calendar(
                vevent=[
                    Event(
                        summary="Test event",
                        dtstart=datetime(2022, 8, 31),
                        dtend=datetime(2022, 8, 31) + timedelta(hours=1),
                    )
                ],
            ),
            CalendarEvent(
                filepath="test.ics",
                summary="Test event",
                event_date=datetime(2022, 8, 31).date(),
            ),
        ),
        (
            Calendar(
                vevent=[
                    Event(
                        summary="Test event",
                        dtstart=None,
                    )
                ],
            ),
            ValueError("No start date."),
        ),
        (
            Calendar(
                vevent=[
                    Event(
                        summary="Test event",
                        dtstart=datetime(2022, 8, 31),
                    )
                ],
                vtodo=[Todo()],
            ),
            ValueError("Is a TODO file."),
        ),
        (
            Calendar(
                vevent=[
                    Event(
                        summary="Test event",
                        dtstart=datetime(2022, 8, 31),
                        rrule=Recur(freq=Frequency.DAILY, count=3),
                    )
                ],
            ),
            ValueError("Is repeating."),
        ),
        (
            Calendar(
                vevent=[
                    Event(
                        summary="Test event",
                        dtstart=datetime(2022, 8, 30),
                    ),
                    Event(
                        summary="Test event",
                        dtstart=datetime(2022, 8, 31),
                    ),
                ],
            ),
            ValueError("Is not single event."),
        ),
    ],
)
def test_transform_to_calendar_event(
    calendar: Calendar,
    expected: CalendarEvent,
):
    """Test transformation logic."""

    calendar_event = transform_to_calendar_event(
        filepath="test.ics",
        calendar=calendar,
    )

    assert str(calendar_event) == str(expected)
