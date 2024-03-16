import importlib
import click

from epic_events_crm.authentication import log_in, requires_auth, get_current_user
from epic_events_crm.permissions import requires_permissions
from epic_events_crm.controllers.employees import EmployeeController
from epic_events_crm.controllers.clients import ClientController

NEEDED_MODULES = (
    "epic_events_crm.models.departments_permissions",
    "epic_events_crm.models.clients",
    "epic_events_crm.models.contracts",
    "epic_events_crm.models.events",
    "epic_events_crm.models.employees",
)
for module in NEEDED_MODULES:
    try:
        importlib.import_module(module)
    except Exception as e:
        print(f"Could not import module {module}.")
        print(f"Error: {e}")


@click.group()
def eecrm():
    pass


@eecrm.command(name="login", short_help="Log in an employee.")
@click.argument("email")
@click.option("--password", "-p", prompt=True, hide_input=True)
def login(email, password):
    if log_in(email, password):
        click.echo("Logged in for 15 minutes.")
    else:
        click.echo("Invalid credentials.")


@eecrm.command(name="add-emp", short_help="Add an employee.")
@click.argument("firstname")
@click.argument("lastname")
@click.argument("email")
@click.argument("department_id", type=int)
@click.password_option("--password", "-p")
@requires_auth
@requires_permissions(["create_employee"])
def create_employee(
    firstname: str, lastname: str, email: str, department_id: int, password: str
) -> None:
    """
    Create an employee and add it to the database. Do not use the --password option if
    you don't want it to be visible in the terminal, it will prompt for it.
    """
    employee_controller = EmployeeController()
    try:
        employee_controller.create(
            fname=firstname,
            lname=lastname,
            email=email,
            password=password,
            department_id=department_id,
        )
        click.echo(f"Employee {firstname} {lastname} ({email}) created.")
    except Exception as e:
        click.echo(f"Error: {e}")


@eecrm.command(name="update-emp", short_help="Update an employee.")
@click.option("--empid", "-id", type=int, help="Employee id.")
@click.option("--email", "-e", help="Employee email (or new email if id is provided).")
@click.option("--fname", "-fn", help="New first name.")
@click.option("--lname", "-ln", help="New last name.")
@click.option("--did", "-d", type=int, help="New department id.")
@requires_auth
@requires_permissions(["update_employee"])
def update_employee(empid, email, fname, lname, did):
    """
    Update an employee's details. Employee is identified by id or email.
    id takes precedence over email if both are provided and is needed to update email.
    """
    employee_controller = EmployeeController()
    try:
        employee_controller.update(
            employee_id=empid, email=email, fname=fname, lname=lname, department_id=did
        )
        click.echo("Employee updated.")
    except Exception as e:
        click.echo(f"Error: {e}")


@eecrm.command(name="delete-emp", short_help="Delete an employee.")
@click.option("--empid", "-id", type=int, help="Employee id.")
@click.option("--email", "-e", help="Employee email.")
@requires_auth
@requires_permissions(["delete_employee"])
def delete_employee(empid, email):
    """Delete an employee. Employee is identified by id or email."""
    employee_controller = EmployeeController()
    # Get employee by id or email
    if empid is not None:
        employee = employee_controller.repo.get_by_id(empid)
    elif email is not None:
        employee = employee_controller.repo.get_by_email(email)
    else:
        click.echo("Provide either id or email.")
        return

    if employee is None:
        click.echo("Employee not found.")
        return
    # Confirm deletion of the right employee before proceeding
    else:
        if click.confirm(f"Please confirm deletion of {employee}", abort=True):
            try:
                employee_controller.delete(employee)
                click.echo("Employee successfully deleted.")
            except Exception as e:
                click.echo(f"Error: {e}")


@eecrm.command(name="add-client", short_help="Add a client.")
@click.argument("firstname")
@click.argument("lastname")
@click.argument("email")
@click.option("--phone", "-p", help="Client phone number.")
@click.option("--company", "-c", help="Client company name.")
@requires_auth
@requires_permissions(["create_client"])
def create_client(firstname: str, lastname: str, email: str, phone: str, company: str):
    """
    Create a client and add it to the database. The salesperson is automatically set to
    the one who creates the client.
    """
    client_controller = ClientController()
    current_user = get_current_user()  # only salespeople can create clients
    try:
        client_controller.create(
            fname=firstname,
            lname=lastname,
            email=email,
            phone=phone,
            company_name=company,
            salesperson_id=current_user.id,
        )
        click.echo(f"Client {firstname} {lastname} ({email}) created.")
    except Exception as e:
        click.echo(f"Error: {e}")


@eecrm.command(name="update-client", short_help="Update a client.")
@click.option("--clientid", "-id", type=int, help="Client id.")
@click.option("--email", "-e", help="Client email (or new email if id is provided).")
@click.option("--fname", "-fn", help="New first name.")
@click.option("--lname", "-ln", help="New last name.")
@click.option("--salesid", "-s", type=int, help="New salesperson id.")
@click.option("--phone", "-p", help="New phone number.")
@click.option("--company", "-c", help="New company name.")
@requires_auth
@requires_permissions(["update_client"])
def update_client(clientid, email, fname, lname, salesid, phone, company):
    """
    Update a client's details. Client is identified by id or email.
    id takes precedence over email if both are provided and is needed to update email.
    """
    client_controller = ClientController()
    try:
        client_controller.update(
            client_id=clientid,
            email=email,
            fname=fname,
            lname=lname,
            salesperson_id=salesid,
            phone=phone,
            company_name=company,
        )
        click.echo("Client updated.")
    except Exception as e:
        click.echo(f"Error: {e}")


@eecrm.command(name="delete-client", short_help="Delete a client.")
@click.option("--clientid", "-id", type=int, help="Client id.")
@click.option("--email", "-e", help="Client email.")
@requires_auth
@requires_permissions(["delete_client"])
def delete_client(clientid, email):
    """Delete a client. Client is identified by id or email."""
    client_controller = ClientController()
    # Get client by id or email
    if clientid is not None:
        client = client_controller.repo.get_by_id(clientid)
    elif email is not None:
        client = client_controller.repo.get_by_email(email)
    else:
        click.echo("Provide either id or email.")
        return

    if client is None:
        click.echo("Client not found.")
        return
    # Confirm deletion of the right client before proceeding
    else:
        if click.confirm(f"Please confirm deletion of {client}", abort=True):
            try:
                client_controller.delete(client)
                click.echo("Client successfully deleted.")
            except Exception as e:
                click.echo(f"Error: {e}")


if __name__ == "__main__":
    eecrm()
