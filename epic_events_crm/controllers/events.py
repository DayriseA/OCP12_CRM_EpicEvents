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
        # Create event
        event = Event(
            name=name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            address_line1=address_line,
            city=city,
            country=country,
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
