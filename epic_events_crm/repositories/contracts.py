from typing import Optional
from sqlalchemy import select, union

from epic_events_crm.database import get_session
from epic_events_crm.models.contracts import Contract
from epic_events_crm.models.clients import Client
from epic_events_crm.models.events import Event


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

    def get_unsigned(self):
        """Return all unsigned contracts."""
        try:
            return (
                self.session.execute(select(Contract).filter_by(signed=False))
                .scalars()
                .all()
            )
        except Exception as e:
            print(f"Error getting unsigned contracts: {e}")

    def get_unpaid(self):
        """Return all contracts still not fully paid."""
        try:
            return (
                self.session.execute(select(Contract).filter(Contract.due_amount > 0))
                .scalars()
                .all()
            )
        except Exception as e:
            print(f"Error getting unpaid contracts: {e}")

    def get_unsigned_or_unpaid(self):
        """Return all contracts that are either unsigned or not fully paid."""
        try:
            unsigned = select(Contract).filter_by(signed=False)
            unpaid = select(Contract).filter(Contract.due_amount > 0)
            # Deprecated way of doing it
            # return (
            #     self.session.query(Contract)
            #     .from_statement(union(unsigned, unpaid))
            #     .all()
            # )

            # Recommended way since SQLAlchemy 2.0
            return self.session.scalars(
                select(Contract).from_statement(union(unsigned, unpaid))
            ).all()
        except Exception as e:
            print(f"Error getting unsigned or unpaid contracts: {e}")

    def get_by_salesperson(self, salesperson_id: int):
        """Return all contracts related to the clients of a given salesperson."""
        try:
            return (
                self.session.execute(
                    select(Contract)
                    .join(Client)
                    .filter(Client.salesperson_id == salesperson_id)
                )
                .scalars()
                .all()
            )
        except Exception as e:
            print(f"Error getting contracts by salesperson: {e}")

    def get_without_event(self):
        """Return all contracts without an event."""
        try:
            return (
                self.session.execute(
                    select(Contract)
                    .outerjoin(Event, Contract.id == Event.contract_id)
                    .filter(Event.contract_id == None)  # noqa: E711
                )
                .scalars()
                .all()
            )
        except Exception as e:
            print(f"Error getting contracts without event: {e}")

    def get_by_salesperson_and_wo_event(self, salesperson_id: int):
        """Return all contracts without an event and related to a salesperson."""
        try:
            return (
                self.session.execute(
                    select(Contract)
                    .join(Client)
                    .outerjoin(Event, Contract.id == Event.contract_id)
                    .filter(
                        Client.salesperson_id == salesperson_id,
                        Event.contract_id == None,  # noqa: E711
                    )
                )
                .scalars()
                .all()
            )
        except Exception as e:
            print(f"Error getting contracts by salesperson and without event: {e}")
