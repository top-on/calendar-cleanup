"""Functions for loading data."""

from ical.calendar import Calendar
from ical.calendar_stream import CalendarParseError, IcsCalendarStream
from webdav4.client import Client


def list_ics_filepaths(client: Client) -> list[str]:
    """
    Lists the filenames of .ICS files.

    Returns:
        A list of filenames.
    """
    print("\nListing WebDAV files...")
    files = client.ls(path=".")
    print(f"Found {len(files)} WebDAV files.")

    filenames = [
        file["name"]
        for file in files
        if isinstance(file["name"], str) and file["name"].endswith(".ics")
    ]
    return filenames


def load_ics_content(
    ics_filepaths: list[str],
    client: Client,
) -> list[str]:
    """
    Load the content of the specified ICS files.

    Args:
        ics_filepaths (list[str]): List of filepaths of the ICS files.
    Returns:
        list[str]: List of file contents of the ICS files. Has same length as input.
    Raises:
        AssertionError: If input and output do not have same length.
    """
    print("\nReading WebDAV files' content...")

    file_contents: list[str] = []
    for filepath in ics_filepaths:
        print(f"Reading content from '{filepath}'...")
        with client.open(filepath, "r") as f:
            file_contents.append(f.read())

    print(f"Downloaded {len(file_contents)} WebDAV files.")
    assert len(file_contents) == len(ics_filepaths), "Input and output not same length."
    return file_contents


def parse_ics_content(
    ics_filepaths: list[str],
    file_contents: list[str],
) -> list[tuple[str, Calendar]]:
    """
    Parses the content of ICS files.

    Args:
        ics_filepaths (list[str]): List of filepaths of the ICS files.
        file_contents (list[str]): List of contents of the ICS files.
    Returns:
        list[tuple[str, Calendar]]:
            List of tuples with filepath and parsed Calendar object for each ICS file.
            Entities that could not be parsed are not included in the list.
    """
    print("\nParsing ICS content...")
    filenames_calendars: list[tuple[str, Calendar]] = []
    for filepath, file_content in zip(ics_filepaths, file_contents):
        try:
            print(f"Parsing ICS file '{filepath}'...")
            calendar = IcsCalendarStream.calendar_from_ics(file_content)
            filenames_calendars.append((filepath, calendar))
        except CalendarParseError as e:
            print(f"Failed to parse file {filepath}: {e}. Next.")
            continue

    print(f"Parsed {len(filenames_calendars)} ICS files.")
    return filenames_calendars
