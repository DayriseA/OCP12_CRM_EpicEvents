from typing import Optional
from sqlalchemy import exc

from epic_events_crm.utilities import (
    is_email_valid,
    is_phone_valid,
    remove_spaces_and_hyphens,
)
from epic_events_crm.database import get_session
from epic_events_crm.models.clients import Client
from epic_events_crm.repositories.clients import ClientRepo
from epic_events_crm.controllers.employees import EmployeeController


class ClientController:
    """
    Client controller. If no session is provided to constructor, a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()
        self.repo = ClientRepo(self.session)
        self.employee_controller = EmployeeController(self.session)

    def create(
        self,
        fname: str,
        lname: str,
        email: str,
        salesperson_id: int,
        phone: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> None:
        """Create a client and add it to the database."""
        # Check if email is valid
        if not is_email_valid(email):
            raise ValueError("Invalid email.")
        # Check if email is not already used
        if self.repo.get_by_email(email):
            raise ValueError("Email already in use.")
        # Check if phone is valid and not already used
        if phone:
            phone = remove_spaces_and_hyphens(phone)
            if not is_phone_valid(phone):
                raise ValueError("Invalid phone number.")
            if self.repo.get_by_phone(phone):
                raise ValueError("Phone number already in use.")
        # Format first and last name
        fname = fname.title()
        lname = lname.upper()

        client = Client(
            fname=fname,
            lname=lname,
            email=email,
            salesperson_id=salesperson_id,
            phone=phone,
            company_name=company_name,
        )
        self.repo.add(client)
        try:
            self.session.commit()
        except exc.SQLAlchemyError as e:
            raise exc.SQLAlchemyError(f"Error: {e}")

    def update(
        self,
        client_id: Optional[int] = None,
        email: Optional[str] = None,
        fname: Optional[str] = None,
        lname: Optional[str] = None,
        salesperson_id: Optional[int] = None,
        phone: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> None:
        """
        Update a client's details. Identify client by id or email.
        """
        if not client_id and not email:
            raise ValueError("Provide either client id or email.")

        # Get client by id or email
        if client_id is not None:
            client = self.repo.get_by_id(client_id)
            # If client id and email are provided, update email (if valid)
            if email is not None:
                if is_email_valid(email) and not self.repo.get_by_email(email):
                    client.email = email
                else:
                    raise ValueError("Email invalid or already used.")
        else:
            client = self.repo.get_by_email(email)
        if client is None:
            raise ValueError("Client not found.")

        # Update client details
        if fname:
            client.fname = fname.title()
        if lname:
            client.lname = lname.upper()

        if salesperson_id:
            # Check if salesperson exists and is indeed a salesperson
            salesperson = self.employee_controller.repo.get_by_id(salesperson_id)
            if not salesperson:
                raise ValueError("Employee not found.")
            if salesperson.department.name != "Sales":
                raise ValueError("Employee must be a salesperson.")
            # Update salesperson
            client.salesperson_id = salesperson_id

        if phone:
            phone = remove_spaces_and_hyphens(phone)
            if is_phone_valid(phone) and not self.repo.get_by_phone(phone):
                client.phone = phone
            else:
                raise ValueError("Phone number invalid or already used.")
        if company_name:
            client.company_name = company_name
        try:
            self.session.commit()
        except exc.SQLAlchemyError as e:
            raise exc.SQLAlchemyError(f"Error: {e}")

    def delete(self, client: Client) -> None:
        """Delete a client from the database."""
        self.repo.delete(client)
        try:
            self.session.commit()
        except exc.SQLAlchemyError as e:
            raise exc.SQLAlchemyError(f"Error: {e}")

    def get_all(self):
        return self.repo.get_all()
