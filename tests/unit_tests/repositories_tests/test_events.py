import pytest
from sqlalchemy import inspect

from epic_events_crm.models.events import Event
from epic_events_crm.repositories.events import EventRepo


class TestEventRepo:
    """
    Test EventRepo class.
    Take into account the 'populate_db' fixture from conftest.py.
    """

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup(cls, session):
        cls.repo = EventRepo(session)
        cls.event_kwargs = {
            "name": "Test event 4",
            "start_datetime": "2026-09-01 08:00",
            "end_datetime": "2026-09-01 18:00",
            "address_line1": "77A test avenue",
            "city": "Test City",
            "country": "Testland",
            "postal_code": "1234",
            "attendees_number": "10",
            "notes": "What a wonderful note! Lorem ipsum dolor sit amet.",
            "contract_id": "1",
            "support_person_id": "7",
        }
        cls.created_id = None

    def test_add(self):
        """Test that the event is added to the session."""
        event1 = Event(**self.event_kwargs)
        self.repo.add(event1)
        assert inspect(event1).pending
        self.repo.session.commit()
        assert inspect(event1).persistent
        self.created_id = event1.id

    def test_get_by_id(self):
        """Test that an event is obtained by its id."""
        event = self.repo.get_by_id(1)
        assert isinstance(event, Event)
        assert event.id == 1
        assert event.name == "Event name 1"

    def test_get_all(self):
        """Test that all events are retrieved as a list of Event objects."""
        events = self.repo.get_all()
        assert isinstance(events, list)
        assert all(isinstance(event, Event) for event in events)

    def test_get_events_assigned_to_support_person(self):
        """Test that all events assigned to a support person are retrieved."""
        events = self.repo.get_events_assigned_to(7)
        assert isinstance(events, list)
        assert all(isinstance(event, Event) for event in events)
        assert all(event.support_person_id == 7 for event in events)
        assert len(events) == 2

    def delete(self):
        """Test that the event is marked for deletion in the session."""
        event = self.repo.get_by_id(self.created_id)  # the one created in test_add()
        self.repo.delete(event)
        self.repo.session.flush()
        assert inspect(event).deleted
