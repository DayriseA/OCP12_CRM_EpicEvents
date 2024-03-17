from typing import List, Optional
from sqlalchemy import select

from epic_events_crm.database import get_session
from epic_events_crm.utilities import remove_spaces_and_hyphens
from epic_events_crm.models.clients import Client


class ClientRepo:
    """
    Client repository class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()

    def add(self, client: Client) -> None:
        """Add a client to the session."""
        try:
            self.session.add(client)
        except Exception as e:
            print(f"Error adding client: {e}")

    def get_all(self) -> List[Client]:
        """Return all clients as a list, ordered by company name."""
        try:
            return (
                self.session.execute(select(Client).order_by(Client.company_name))
                .scalars()
                .all()
            )
        except Exception as e:
            print(f"Error getting all clients: {e}")

    def get_by_id(self, client_id: int) -> Optional[Client]:
        """Return a client by its id."""
        try:
            return self.session.get(Client, client_id)
        except Exception as e:
            print(f"Error getting client by id: {e}")

    def get_by_email(self, email: str) -> Optional[Client]:
        """Return a client by its email."""
        try:
            return self.session.execute(
                select(Client).filter_by(email=email)
            ).scalar_one_or_none()
        except Exception as e:
            print(f"Error getting client by email: {e}")

    def get_by_phone(self, phone: str) -> Optional[Client]:
        """Return a client by its phone."""
        phone = remove_spaces_and_hyphens(phone)
        try:
            return self.session.execute(
                select(Client).filter_by(phone=phone)
            ).scalar_one_or_none()
        except Exception as e:
            print(f"Error getting client by phone: {e}")

    def delete(self, client: Client) -> None:
        """Mark a client for deletion in the session."""
        try:
            self.session.delete(client)
        except Exception as e:
            print(f"Error deleting client: {e}")

    def get_clients_assigned_to(self, salesperson_id=None) -> List[Client]:
        """
        Return all clients assigned to a specified (by id) salesperson.
        If no id is provided, return all clients without a salesperson.
        """
        try:
            return (
                self.session.execute(
                    select(Client).filter(Client.salesperson_id == salesperson_id)
                )
                .scalars()
                .all()
            )
        except Exception as e:
            print(f"Error: {e}")
