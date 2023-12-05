"""Model schema for calendar_cleanup app."""


from pydantic import BaseModel


class Credentials(BaseModel):
    """Credentials for the database."""

    username: str
    password: str
    webdav_url: str
