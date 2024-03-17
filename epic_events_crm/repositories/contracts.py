from typing import Optional
from sqlalchemy import select

from epic_events_crm.database import get_session
from epic_events_crm.models.contracts import Contract


class ContractRepo:
    """
    Contract repository class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()

    def add(self, contract: Contract) -> None:
        """Add a contract to the session."""
        try:
            self.session.add(contract)
        except Exception as e:
            print(f"Error adding contract: {e}")

    def get_by_id(self, contract_id: int) -> Optional[Contract]:
        """Return a contract by its id."""
        try:
            return self.session.get(Contract, contract_id)
        except Exception as e:
            print(f"Error getting contract by id: {e}")

    def delete(self, contract: Contract) -> None:
        """Mark a contract for deletion in the session."""
        try:
            self.session.delete(contract)
        except Exception as e:
            print(f"Error deleting contract: {e}")

    def get_all(self):
        """Return all contracts."""
        try:
            return self.session.execute(select(Contract)).scalars().all()
        except Exception as e:
            print(f"Error getting all contracts: {e}")
