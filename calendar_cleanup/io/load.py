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


def load_ics_content(ics_filepaths: list[str], client: Client) -> list[str]:
    """
    Load the content of the specified ICS files.

    Args:
        ics_filepaths (list[str]): List of filepaths of the ICS files.
    Returns:
        list[str]: List of file contents of the ICS files.
    """
    print("\nReading WebDAV files' content...")

    file_contents: list[str] = []
    for filepath in ics_filepaths:
        print(f"Reading content from '{filepath}'...")
        with client.open(filepath, "r") as f:
            file_contents.append(f.read())

    print(f"Downloaded {len(file_contents)} WebDAV files.")
    return file_contents
