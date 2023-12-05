"""Functions for authorizing the user."""

from getpass import getpass

from webdav4.client import Client, HTTPError

from calendar_cleanup.schema import Credentials


def request_credentials() -> Credentials:
    """Request credentials from the user.

    This function prompts the user to enter their username, password, and calendar URL.
    It then creates and returns a `Credentials` object with the provided information.

    Returns:
        Credentials: The user's credentials for accessing the WebDAV calendar.
    """
    print("Please enter the credentials for your WebDAV calendar.")
    username = input("username: ")
    password = getpass("password: ")

    # read input for url with a default
    default_url = f"https://posteo.de:8443/calendars/{username}/default"
    url = input(f"Calendar URL [{default_url}]: ") or default_url

    credentials = Credentials(username=username, password=password, webdav_url=url)
    return credentials


def create_webdav_client(credentials: Credentials) -> Client:
    """
    Create a WebDAV client using the provided credentials.

    Args:
        credentials (Credentials): The credentials for authentication.
    Returns:
        Client: The WebDAV client.
    Raises:
        HTTPError: If authentication with the WebDAV server fails.
    """
    client = Client(
        base_url=credentials.webdav_url,
        auth=(credentials.username, credentials.password),
    )

    print("Verifying authentication...")
    try:
        client.exists(".")  # verify authentication
    except HTTPError as e:
        print(f"Authentication with WebDAV server failed: '{e}'. Exiting.")
        exit(1)
    print("Authentication successful.")

    return client
