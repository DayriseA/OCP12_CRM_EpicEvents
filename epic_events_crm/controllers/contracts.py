from sqlalchemy import exc
from pymysql.err import IntegrityError
from typing import Optional
from decimal import Decimal

from epic_events_crm.database import get_session
from epic_events_crm.authentication import get_current_user
from epic_events_crm.models.contracts import Contract
from epic_events_crm.repositories.contracts import ContractRepo


class ContractController:
    """
    Contract Controller. If no session is provided to constructor, a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()
        self.repo = ContractRepo(self.session)

    def create(self, client_id: int, due_amount: float) -> None:
        """Create a contract and add it to the database."""
        contract = Contract(
            client_id=client_id, total_amount=due_amount, due_amount=due_amount
        )
        self.repo.add(contract)
        try:
            self.session.commit()
        except exc.SQLAlchemyError as e:
            msg = "a foreign key constraint fails"  # Client id not found
            if isinstance(e.orig, IntegrityError) and msg in e.orig.args[1]:
                raise exc.SQLAlchemyError("IntegrityError: Please check client id.")
            raise exc.SQLAlchemyError(f"Error: {e}")

    def update(
        self,
        contract_id: int,
        total_amount: Optional[float],
        paid_amount: Optional[float],
        signed: Optional[bool],
        client_email: Optional[str],
    ) -> None:
        """
        Update a contract's details.
        Salesperson can only update contracts of their clients.
        """
        contract = self.repo.get_by_id(contract_id)
        if contract is None:
            raise ValueError("Contract not found.")

        # Check if the current user is a salesperson
        employee = get_current_user()
        if employee.department.name == "Sales":
            # and if the contract is tied to one of their clients
            if employee.id != contract.client.salesperson_id:
                raise ValueError("You can only update contracts of your clients.")

        # Update of total amount implies update of due amount
        if total_amount is not None:
            total_amount = Decimal(total_amount)  # Contract model uses Decimal(15, 2)
            difference = total_amount - contract.total_amount
            contract.total_amount = total_amount
            contract.due_amount += difference
        # Money paid implies reduction of due amount
        if paid_amount is not None:
            paid_amount = Decimal(paid_amount)  # Contract model uses Decimal(15, 2)
            contract.due_amount -= paid_amount
        # Update signed status
        if signed is not None:
            contract.signed = signed

        if client_email is not None:
            # Check if client exists
            from epic_events_crm.repositories.clients import ClientRepo

            client_repo = ClientRepo(self.session)
            client = client_repo.get_by_email(client_email)
            if client is None:
                raise ValueError("Client not found.")
            old_client = contract.client
            contract.client_id = client.id
            print(f"Trying to change client from {old_client} to {client}")

        # If due amount is negative, inform user
        if contract.due_amount < 0:
            print(f"Please note that due amount is negative: {contract.due_amount}")
        try:
            self.session.commit()
        except exc.SQLAlchemyError as e:
            raise exc.SQLAlchemyError(f"Error: {e}")

    def get_all(self):
        """Return a list of all contracts."""
        return self.repo.get_all()
