"""Functions for loading data."""

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
