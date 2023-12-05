"""Model schema for calendar_cleanup app."""

from datetime import date

from pydantic import BaseModel


class Credentials(BaseModel):
    """Credentials for the database."""

    username: str
    password: str
    webdav_url: str


class CalendarEvent(BaseModel):
    """A calendar event."""

    filepath: str
    summary: str
    event_date: date
