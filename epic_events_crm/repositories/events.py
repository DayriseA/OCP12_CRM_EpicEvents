from typing import Optional

from epic_events_crm.database import get_session
from epic_events_crm.models.events import Event


class EventRepo:
    """
    Event repository class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()

    def add(self, event: Event) -> None:
        """Add an event to the session."""
        try:
            self.session.add(event)
        except Exception as e:
            print(f"Error adding event: {e}")

    def get_by_id(self, event_id: int) -> Optional[Event]:
        """Return an event by its id."""
        try:
            return self.session.get(Event, event_id)
        except Exception as e:
            print(f"Error getting event by id: {e}")

    def delete(self, event: Event) -> None:
        """Mark an event for deletion in the session."""
        try:
            self.session.delete(event)
        except Exception as e:
            print(f"Error deleting event: {e}")
