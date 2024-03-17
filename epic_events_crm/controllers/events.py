from typing import Optional
from datetime import datetime

from epic_events_crm.database import get_session
from epic_events_crm.models.events import Event
from epic_events_crm.repositories.events import EventRepo
from epic_events_crm.repositories.contracts import ContractRepo


class EventController:
    """
    Event controller. If no session is provided to constructor, a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()
        self.repo = EventRepo(self.session)

    def create(
        self,
        name: str,
        start_date: str,
        end_date: str,
        address_line: str,
        city: str,
        country: str,
        postal_code: str,
        attendees_number: int,
        contract_id: int,
        notes: Optional[str] = None,
    ) -> None:
        """Create an event and add it to the database."""
        # Check if contract exists
        contract_repo = ContractRepo(self.session)
        contract = contract_repo.get_by_id(contract_id)
        if contract is None:
            raise ValueError("Contract not found.")
        # Convert dates to datetime if in expected format (YYYY-MM-DD HH:MM)
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD HH:MM'.")
        # Check if start date is before end date
        if start_datetime >= end_datetime:
            raise ValueError("Start date must be before end date.")
        # Let's add a date to the notes
        if notes is not None:
            dt = datetime.now()
            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
            notes = f"{formatted_date}:\n {notes}"
        # Create event
        event = Event(
            name=name.capitalize(),
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            address_line1=address_line,
            city=city.title(),
            country=country.upper(),
            postal_code=postal_code,
            attendees_number=attendees_number,
            contract_id=contract_id,
            notes=notes,
        )
        self.repo.add(event)
        try:
            self.session.commit()
        except Exception as e:
            raise ValueError(f"Error: {e}")

    def update(
        self,
        event_id: int,
        name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        address_line: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None,
        attendees_number: Optional[int] = None,
        notes: Optional[str] = None,
        append: Optional[bool] = False,
        support_person_id: Optional[int] = None,
    ) -> None:
        """Update an event's details."""
        event = self.repo.get_by_id(event_id)
        if event is None:
            raise ValueError("Event not found.")
        # Convert dates to datetime if in expected format (YYYY-MM-DD HH:MM)
        if start_date is not None:
            try:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
                event.start_datetime = start_datetime
            except ValueError:
                raise ValueError("Invalid date format. Use 'YYYY-MM-DD HH:MM'.")
        if end_date is not None:
            try:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
                event.end_datetime = end_datetime
            except ValueError:
                raise ValueError("Invalid date format. Use 'YYYY-MM-DD HH:MM'.")
        # Check if start date is before end date
        if event.start_datetime >= event.end_datetime:
            raise ValueError("Start date must be before end date.")
        # Update event's details
        if name is not None:
            event.name = name.capitalize()
        if address_line is not None:
            event.address_line1 = address_line
        if city is not None:
            event.city = city.title()
        if country is not None:
            event.country = country.upper()
        if postal_code is not None:
            event.postal_code = postal_code
        if attendees_number is not None:
            event.attendees_number = attendees_number

        if notes is not None:
            dt = datetime.now()
            formatted_date = dt.strftime("%Y-%m-%d %H:%M")
            notes = f"{formatted_date}:\n {notes}"
            # Adapt behavior if append is True or False
            if append:
                # += operator can't be used if notes is None
                if event.notes is None:
                    event.notes = notes
                else:
                    event.notes += f"\n{notes}"
            else:
                event.notes = notes

        if support_person_id is not None:
            # Check if support person exists and is indeed a support person
            from epic_events_crm.repositories.employees import EmployeeRepo

            employee_repo = EmployeeRepo(self.session)
            support_person = employee_repo.get_by_id(support_person_id)
            if support_person is None:
                raise ValueError("Support person not found.")
            if support_person.department.name != "Support":
                raise ValueError("Employee is not from support department.")
            event.support_person_id = support_person_id
        try:
            self.session.commit()
        except Exception as e:
            raise ValueError(f"Error: {e}")
