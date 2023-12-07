"""Funcations for deleting event files."""


from webdav4.client import Client

from calendar_cleanup.schema import CalendarEvent


def sort_and_print_events(calendar_events: list[CalendarEvent]) -> list[CalendarEvent]:
    """Sort and output the list of Calendar Events that can be deleted.

    Args:
        calendar_events:
            A list of Calender Events that meet requirements for deletion.
    Returns:
        The sorted list of Calendar Events.
    """
    # sort events by date
    calendar_events_sorted = sorted(
        calendar_events,
        key=lambda x: x.event_date,
    )

    print("\nEvents that can be deleted:")
    for calendar_event in calendar_events_sorted:
        print(f"- {str(calendar_event.event_date)}: {calendar_event.summary}")
    return calendar_events_sorted


def confirm_and_delete_events(
    calendar_events: list[CalendarEvent],
    client: Client,
) -> None:
    """
    Ask user for confirmation, when delete the listed Calendar Events.

    Args:
        calendar_events: Calendar Events that can be deleted.
    """
    if input("\nDelete listed events? [y/N] ").lower() == "y":
        print("Deletion confirmed. Deleting events...")
    else:
        print("Deletion not confirmed. Exiting.")
        return  # exit if user did not confirm

    for calendar_event in calendar_events:
        print(f"Deleting event: '{calendar_event.summary}' ...")
        client.remove(calendar_event.filepath)
    print("Deletion completed.")
