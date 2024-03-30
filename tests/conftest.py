import os
import pytest
from dotenv import load_dotenv
from alembic import command
from alembic.config import Config
from sqlalchemy import delete

from epic_events_crm.database import get_test_session
from epic_events_crm.views.base import BaseView

view = BaseView()


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    """Run the alembic migrations on the test database."""
    load_dotenv()
    config = Config("alembic.ini")  # Tests run from the root directory
    db_test_name = os.getenv("DB_TEST_NAME")
    config.set_main_option("sqlalchemy.database", db_test_name)
    view.display_as(f"\nUPGRADING MIGRATIONS ON: {db_test_name}", "info")
    command.upgrade(config, "head")

    yield

    view.display_as(f"\nDOWNGRADING MIGRATIONS ON: {db_test_name}", "info")
    command.downgrade(config, "base")


@pytest.fixture(scope="class")
def session():
    """Provide a test session as a fixture at a class scope."""
    session = get_test_session()

    yield session

    session.rollback()  # avoid sqlalchemy.exc.PendingRollbackError
    session.close()


employees_kwargs = [
    {
        # 1
        "fname": "Admin",
        "lname": "ADMIN",
        "email": "admin@admin.com",
        "password": "Passw0rd",
        "department_id": "1",
    },
    {
        # 2
        "fname": "Lionel",
        "lname": "FERR",
        "email": "flionel@manager.com",
        "password": "Passw0rd",
        "department_id": "2",
    },
    {
        # 3
        "fname": "Sabrina",
        "lname": "HEURT",
        "email": "hsabrina@manager.com",
        "password": "Passw0rd",
        "department_id": "2",
    },
    {
        # 4
        "fname": "Quentin",
        "lname": "ACHARD",
        "email": "aquentin@sales.com",
        "password": "Passw0rd",
        "department_id": "3",
    },
    {
        # 5
        "fname": "Valentin",
        "lname": "DUDEK",
        "email": "dvalentin@sales.com",
        "password": "Passw0rd",
        "department_id": "3",
    },
    {
        # 6
        "fname": "Mercedes",
        "lname": "PINAR",
        "email": "pmercedes@supp.com",
        "password": "Passw0rd",
        "department_id": "4",
    },
    {
        # 7
        "fname": "Anne",
        "lname": "SOPA",
        "email": "sanne@supp.com",
        "password": "Passw0rd",
        "department_id": "4",
    },
]

clients_kwargs = [
    {
        "fname": "John",
        "lname": "DOE",
        "email": "jdoe@mail.com",
        "phone": "1234567890",
        "company_name": "Doe Inc.",
        "salesperson_id": 4,
    },
    {
        "fname": "Jane",
        "lname": "DAE",
        "email": "jdae@mail.com",
        "phone": "0123456789",
        "salesperson_id": 4,
    },
    {
        "fname": "Sophie",
        "lname": "GEORGES",
        "email": "gsophie@mail.com",
        "company_name": "Georges & Co.",
        "salesperson_id": 4,
    },
    {
        "fname": "Lyah",
        "lname": "BALI",
        "email": "blyah@mail.com",
        "salesperson_id": 5,
    },
]

contracts_kwargs = [
    {
        "client_id": 1,
        "total_amount": 10000,
        "due_amount": 10000,
        "signed": False,
    },
    {
        "client_id": 2,
        "total_amount": 1000.00,
        "due_amount": 1000.00,
        "signed": False,
    },
    {
        "client_id": 3,
        "total_amount": 2000,
        "due_amount": 0,
        "signed": True,
    },
    {
        "client_id": 3,
        "total_amount": 2500.00,
        "due_amount": 2500.00,
        "signed": False,
    },
    {
        "client_id": 4,
        "total_amount": 3000,
        "due_amount": 1000,
        "signed": True,
    },
    {
        "client_id": 4,
        "total_amount": 5000,
        "due_amount": 5000,
        "signed": True,
    },
]

events_kwargs = [
    {
        "name": "Event name 1",
        "start_datetime": "2026-01-01 08:00",
        "end_datetime": "2026-01-02 18:00",
        "address_line1": "69 rue Sophie Fic",
        "city": "Sophia Antipolis",
        "country": "France",
        "postal_code": "34567",
        "attendees_number": "12",
        "notes": "Sa couleur préférée est le rose fluo.",
        "contract_id": "3",
        "support_person_id": "6",
    },
    {
        "name": "Event name 2",
        "start_datetime": "2026-02-01 08:00",
        "end_datetime": "2026-02-01 18:00",
        "address_line1": "69 rue de la teuf",
        "city": "Fun City",
        "country": "Dreamland",
        "postal_code": "6969",
        "attendees_number": "69",
        "contract_id": "5",
        "support_person_id": "7",
    },
    {
        "name": "Event name 3",
        "start_datetime": "2026-07-01 08:00",
        "end_datetime": "2026-08-01 18:00",
        "address_line1": "77A beach avenue",
        "city": "Beach City",
        "country": "Dreamland",
        "postal_code": "7878",
        "attendees_number": "8",
        "notes": "What a wonderful note! Lorem ipsum dolor sit amet.",
        "contract_id": "6",
    },
]


@pytest.fixture(scope="session", autouse=True)
def populate_db(run_migrations):
    """Populate the test database."""
    from epic_events_crm.models.employees import Employee
    from epic_events_crm.models.clients import Client
    from epic_events_crm.models.contracts import Contract
    from epic_events_crm.models.events import Event

    view.display_as("\nPOPULATING DATABASE", "info")
    session = get_test_session()

    for employee_kwargs in employees_kwargs:
        employee = Employee(**employee_kwargs)
        session.add(employee)
    session.commit()

    for client_kwargs in clients_kwargs:
        client = Client(**client_kwargs)
        session.add(client)
    session.commit()

    for contract_kwargs in contracts_kwargs:
        contract = Contract(**contract_kwargs)
        session.add(contract)
    session.commit()

    for event_kwargs in events_kwargs:
        event = Event(**event_kwargs)
        session.add(event)
    session.commit()

    yield

    session.rollback()  # avoid possible sqlalchemy.exc.PendingRollbackError

    view.display_as("\nDELETING DATA", "info")
    session.execute(delete(Event))
    session.execute(delete(Contract))
    session.execute(delete(Client))
    session.execute(delete(Employee))
    session.commit()
    session.close()
