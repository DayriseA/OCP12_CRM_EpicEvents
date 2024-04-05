import pytest
from datetime import datetime
from typing import Optional

from epic_events_crm.models.events import Event
from epic_events_crm.controllers.events import EventController
from epic_events_crm.authentication import log_in, valid_token_in_env
from epic_events_crm.models.employees import Employee
from epic_events_crm.repositories.employees import EmployeeRepo


class TestEventController:
    """
    Test EventController class.
    Take into account the 'populate_db' fixture from conftest.py.
    """

    # declare valid variables for an event creation:
    c_name = "Test Event"
    c_start_date = "2028-03-13 08:00"
    c_end_date = "2028-03-13 22:00"
    c_address_line = "69 B, Test street"
    c_city = "Test City"
    c_country = "Test Country"
    c_postal_code = "12345"
    c_attendees_number = 100
    c_contract_id = 1
    c_notes = "This is a test note. Lorem ipsum dolor sit amet."
    # define invalid event kwargs that will raise an error:
    unknown_contract_id_kwargs = {
        "name": c_name,
        "start_date": c_start_date,
        "end_date": c_end_date,
        "address_line": c_address_line,
        "city": c_city,
        "country": c_country,
        "postal_code": c_postal_code,
        "attendees_number": c_attendees_number,
        "contract_id": 999,
    }
    already_existing_event_kwargs = {
        "name": c_name,
        "start_date": c_start_date,
        "end_date": c_end_date,
        "address_line": c_address_line,
        "city": c_city,
        "country": c_country,
        "postal_code": c_postal_code,
        "attendees_number": c_attendees_number,
        "contract_id": 3,
    }
    invalid_datetime_format_kwargs = {
        "name": c_name,
        "start_date": "2028-03-13",
        "end_date": "2028/03/14-07:00",
        "address_line": c_address_line,
        "city": c_city,
        "country": c_country,
        "postal_code": c_postal_code,
        "attendees_number": c_attendees_number,
        "contract_id": c_contract_id,
    }
    incoherent_datetimes_kwargs = {
        "name": c_name,
        "start_date": c_end_date,
        "end_date": c_start_date,
        "address_line": c_address_line,
        "city": c_city,
        "country": c_country,
        "postal_code": c_postal_code,
        "attendees_number": c_attendees_number,
        "contract_id": c_contract_id,
    }
    # valid kwargs for an event creation:
    valid_event_kwargs = {
        "name": c_name,
        "start_date": c_start_date,
        "end_date": c_end_date,
        "address_line": c_address_line,
        "city": c_city,
        "country": c_country,
        "postal_code": c_postal_code,
        "attendees_number": c_attendees_number,
        "contract_id": c_contract_id,
        "notes": c_notes,
    }

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup(cls, session):
        cls.controller = EventController(session)
        cls.employee_repo = EmployeeRepo(session)
        cls.created_id = None

        yield
        # delete the created event to not mess with other tests
        event_created = cls.controller.repo.get_by_id(cls.created_id)
        cls.controller.repo.delete(event_created)
        cls.controller.session.commit()

    @pytest.mark.parametrize(
        "event_kwargs, expected",
        [
            (unknown_contract_id_kwargs, ValueError),
            (already_existing_event_kwargs, ValueError),
            (invalid_datetime_format_kwargs, ValueError),
            (incoherent_datetimes_kwargs, ValueError),
        ],
    )
    def test_create_raises_errors(self, event_kwargs, expected):
        """Test that the create method works as expected with wrong parameters."""
        with pytest.raises(expected):
            self.controller.create(**event_kwargs)

    def test_create(self):
        """Test that the event is created and added to the database."""
        event_id = self.controller.create(**self.valid_event_kwargs)
        self.__class__.created_id = event_id  # so other tests can access it

        # check that the event is in the database
        event = self.controller.repo.get_by_id(self.created_id)
        assert event.name == self.c_name.capitalize()
        assert event.start_datetime == datetime.strptime(
            self.c_start_date, "%Y-%m-%d %H:%M"
        )
        assert event.end_datetime == datetime.strptime(
            self.c_end_date, "%Y-%m-%d %H:%M"
        )
        assert event.address_line1 == self.c_address_line
        assert event.city == self.c_city.title()
        assert event.country == self.c_country.upper()
        assert event.postal_code == self.c_postal_code
        assert event.attendees_number == self.c_attendees_number
        assert event.contract_id == self.c_contract_id
        assert self.c_notes in event.notes

    # We need to change the get_current_user method called in the update method so that
    # its tied to the test database and not the actual database
    def get_current_user_test(self) -> Optional[Employee]:
        """Return current user from .env JWT token. Runs against the test database."""
        token = valid_token_in_env()
        if token:
            return self.employee_repo.get_by_id(token["uid"])
        return None

    def test_update_raises_errors(self, mocker):
        """Test that the update method raises the expected errors."""
        # some update logic depends on the current user
        log_in("sanne@supp.com", "Passw0rd", self.employee_repo)

        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.events.get_current_user",
            new=self.get_current_user_test,
        )

        # unknown event id
        with pytest.raises(ValueError):
            self.controller.update(event_id=999, name="New name")
        # event not assigned to the current user (salesperson)
        with pytest.raises(PermissionError):
            self.controller.update(event_id=1, name="New name")
        # change the current user for the remaining tests
        log_in("flionel@manager.com", "Passw0rd", self.employee_repo)
        # invalid datetime format
        with pytest.raises(ValueError):
            self.controller.update(event_id=self.created_id, start_date="JUNE 12 2026")
        with pytest.raises(ValueError):
            self.controller.update(event_id=self.created_id, end_date="2028/08/13")
        # incoherent datetimes
        with pytest.raises(ValueError):
            self.controller.update(event_id=self.created_id, start_date=self.c_end_date)
        # assign to a non-existing person
        with pytest.raises(ValueError):
            self.controller.update(event_id=self.created_id, support_person_id=999)
        # assign to a non-support person
        with pytest.raises(ValueError):
            self.controller.update(event_id=self.created_id, support_person_id=3)

    def test_update(self, mocker):
        """Test that the update method works as expected."""
        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.events.get_current_user",
            new=self.get_current_user_test,
        )
        # still logged in as the manager, assign a support person to the event
        self.controller.update(event_id=self.created_id, support_person_id=7)

        event = self.controller.repo.get_by_id(self.created_id)
        assert event.support_person_id == 7

        # logs as the assigned support person
        log_in("sanne@supp.com", "Passw0rd", self.employee_repo)

        # update the event details
        self.controller.update(
            event_id=self.created_id,
            name="Updated event",
            start_date="2028-03-13 10:00",
            end_date="2028-03-13 20:00",
            address_line="New address",
            city="New City",
            country="New Country",
            postal_code="54321",
            attendees_number=50,
            notes="Updated notes.",
        )
        assert event.name == "Updated event"
        assert event.start_datetime == datetime.strptime(
            "2028-03-13 10:00", "%Y-%m-%d %H:%M"
        )
        assert event.end_datetime == datetime.strptime(
            "2028-03-13 20:00", "%Y-%m-%d %H:%M"
        )
        assert event.address_line1 == "New address"
        assert event.city == "New City"
        assert event.country == "NEW COUNTRY"
        assert event.postal_code == "54321"
        assert event.attendees_number == 50
        assert "Updated notes." in event.notes and self.c_notes not in event.notes

        # check if the append flag works
        self.controller.update(
            event_id=self.created_id, notes="More notes.", append=True
        )
        assert "Updated notes." in event.notes and "More notes." in event.notes

    def test_get_all(self, mocker):
        """Test that all events are returned."""
        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.events.get_current_user",
            new=self.get_current_user_test,
        )
        events = self.controller.get_all()
        assert all(isinstance(event, Event) for event in events)
        assert len(events) == 4

    def test_get_events_assigned_to_current_user(self, mocker):
        """Test that all events assigned to the current user are obtained."""
        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.events.get_current_user",
            new=self.get_current_user_test,
        )

        log_in("sanne@supp.com", "Passw0rd", self.employee_repo)
        events = self.controller.get_events_assigned_to_current_user()
        assert all(event.support_person_id == 7 for event in events)
        assert len(events) == 2

    def test_get_events_without_support(self):
        """Test that all events without a support person are obtained."""
        events = self.controller.get_events_without_support()
        assert isinstance(events, list)
        assert all(event.support_person is None for event in events)
        assert len(events) == 1
