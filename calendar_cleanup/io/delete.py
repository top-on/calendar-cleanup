"""Funcations for deleting event files."""


from datetime import date

from webdav4.client import Client


def sort_and_print_events(
    filenames_summaries_dates_to_delete: list[tuple[str, str, date]]
) -> list[tuple[str, str, date]]:
    """Sort and output the list of events that can be deleted.

    Args:
        filenames_summaries_dates_to_delete:
            A list of (filename, summary, date) for events to delete.
    Returns:
        The sorted list of events, described by (filename, summary, date).
    """
    filenames_summaries_dates_sorted = sorted(
        filenames_summaries_dates_to_delete, key=lambda x: x[2]
    )
    print("\nEvents that can be deleted:")
    for _, summary, event_date in filenames_summaries_dates_sorted:
        print(f"- {str(event_date)}: {summary}")
    return filenames_summaries_dates_sorted


def confirm_and_delete_events(
    filenames_summaries_dates_sorted: list[tuple[str, str, date]],
    client: Client,
) -> None:
    """
    Ask user for confirmation, when delete the listed events.

    Args:
        filenames_summaries_dates_sorted: A list of tuples containing the file path,
            summary, and date of the events to be deleted.
    Returns:
        None
    """
    if input("\nDelete listed events? [y/N] ").lower() == "y":
        print("Deletion confirmed. Deleting events...")
    else:
        print("Deletion not confirmed. Exiting.")
        return  # exit if user did not confirm

    for filepath, summary, _ in filenames_summaries_dates_sorted:  # type: ignore
        print(f"Deleting event: '{summary}' ...")
        client.remove(filepath)
    print("Deletion completed.")
