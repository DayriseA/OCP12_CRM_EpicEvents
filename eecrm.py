import importlib
import click

from epic_events_crm.authentication import log_in, requires_auth, get_current_user
from epic_events_crm.permissions import requires_permissions
from epic_events_crm.controllers.main import MainController
from epic_events_crm.views.main import MainView


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


controller = MainController()
view = MainView()


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


# ############### EMPLOYEES ###############
@eecrm.command(name="add-emp", short_help="Add employee. Options are prompts friendly.")
@click.option("--fname", "-fn", help="First name.", prompt="First name")
@click.option("--lname", "-ln", help="Last name.", prompt="Last name")
@click.option("--email", "-e", help="Email.", prompt="Email")
@click.option("--did", "-d", type=int, help="Department id.", prompt="Department id")
@click.password_option("--password", "-p")
@requires_auth
@requires_permissions(["create_employee"])
def create_employee(
    fname: str, lname: str, email: str, did: int, password: str
) -> None:
    """
    Create an employee and add it to the database. Do not use the --password option if
    you don't want it to be visible in the terminal, it will prompt for it.
    """
    try:
        controller.employees.create(
            fname=fname,
            lname=lname,
            email=email,
            password=password,
            department_id=did,
        )
        click.echo(f"Employee {fname} {lname} ({email}) created.")
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
    try:
        controller.employees.update(
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
    # Get employee by id or email
    if empid is not None:
        employee = controller.employees.repo.get_by_id(empid)
    elif email is not None:
        employee = controller.employees.repo.get_by_email(email)
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
                controller.employees.delete(employee)
                click.echo("Employee successfully deleted.")
            except Exception as e:
                click.echo(f"Error: {e}")


@eecrm.command(name="list-emp", short_help="List employees.")
@requires_auth
def list_employees():
    """List employees."""
    try:
        employees = controller.employees.get_all()
        view.employee.display_employees(employees)
    except Exception as e:
        click.echo(f"Error: {e}")


# ############### CLIENTS ###############
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
    current_user = get_current_user()  # only salespeople can create clients
    try:
        controller.clients.create(
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
    Salespersons can only update clients they are assigned to.
    """
    try:
        controller.clients.update(
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
    # Get client by id or email
    if clientid is not None:
        client = controller.clients.repo.get_by_id(clientid)
    elif email is not None:
        client = controller.clients.repo.get_by_email(email)
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
                controller.clients.delete(client)
                click.echo("Client successfully deleted.")
            except Exception as e:
                click.echo(f"Error: {e}")


@eecrm.command(name="list-clients", short_help="List clients.")
@click.option("--mine", "-m", is_flag=True, help="Clients assigned to current user.")
@requires_auth
def list_clients(mine):
    """List clients. With --mine, list clients assigned to current user."""
    if mine:
        try:
            clients = controller.clients.get_clients_assigned_to_current_user()
            view.client.display_clients(clients)
        except Exception as e:
            click.echo(f"Error: {e}")
    else:
        try:
            clients = controller.clients.get_all()
            view.client.display_clients(clients)
        except Exception as e:
            click.echo(f"Error: {e}")


# ############### CONTRACTS ###############
@eecrm.command(name="add-contract", short_help="Add a contract.")
@click.argument("client_id", type=int)
@click.argument("due_amount", type=float)
@requires_auth
@requires_permissions(["create_contract"])
def create_contract(client_id: int, due_amount: float) -> None:
    """Create a contract and add it to the database."""
    try:
        controller.contracts.create(client_id, due_amount)
        click.echo("Contract created.")
    except Exception as e:
        click.echo(f"Error: {e}")


@eecrm.command(name="update-contract", short_help="Update a contract.")
@click.argument("contract_id", type=int)
@click.option("--amount", "-a", type=float, help="New total amount.")
@click.option("--paid", "-p", type=float, help="Amount paid.")
@click.option("--signed", "-s", type=bool, help="Signed status.")
@click.option("--clientmail", "-c", help="Client email.")
@requires_auth
@requires_permissions(["update_contract"])
def update_contract(contract_id, amount, paid, signed, clientmail):
    """Update a contract's details."""
    try:
        controller.contracts.update(contract_id, amount, paid, signed, clientmail)
        click.echo("Contract updated.")
    except Exception as e:
        click.echo(f"Error: {e}")


@eecrm.command(name="list-contracts", short_help="List contracts.")
@click.option("--unpaid", "-up", is_flag=True, help="List unpaid contracts.")
@click.option("--unsigned", "-us", is_flag=True, help="List unsigned contracts.")
@click.option("--mine", "-m", is_flag=True, help="List contracts on clients of user.")
@click.option("--noevent", "-ne", is_flag=True, help="List contracts without events.")
@requires_auth
def list_contracts(unpaid, unsigned, mine, noevent):
    """
    List contracts. --unpaid, --unsigned and --noevent are mutually exclusive.
    --mine can be used alone or combined with --noevent.
    """
    if mine:
        try:
            contracts = controller.contracts.get_salesperson_supervised(noevent)
            view.contract.display_contracts(contracts)
        except Exception as e:
            click.echo(f"Error: {e}")
    elif unpaid or unsigned or noevent:
        try:
            contracts = controller.contracts.get_depending_on_flags(
                unpaid, unsigned, noevent
            )
            view.contract.display_contracts(contracts)
        except Exception as e:
            click.echo(f"Error: {e}")
    else:
        try:
            contracts = controller.contracts.get_all()
            view.contract.display_contracts(contracts)
        except Exception as e:
            click.echo(f"Error: {e}")


# # ############### EVENTS ###############
@eecrm.command(name="add-event", short_help="Add event. Options are prompts friendly.")
@click.argument("contract_id", type=int)
@click.argument("event_name")
@click.option(
    "--start",
    "-s",
    help="Start date and time (YYYY-MM-DD HH:MM)",
    prompt="Start date and time (YYYY-MM-DD HH:MM)",
)
@click.option(
    "--end",
    "-e",
    help="End date and time (YYYY-MM-DD HH:MM)",
    prompt="End date and time (YYYY-MM-DD HH:MM)",
)
@click.option("--address", "-a", help="Address line.", prompt="Address line")
@click.option("--city", "-c", help="City.", prompt="City")
@click.option("--country", "-C", help="Country.", prompt="Country")
@click.option("--postal", "-p", help="Postal code.", prompt="Postal code")
@click.option(
    "--attendees",
    "-nb",
    type=int,
    help="Number of attendees.",
    prompt="Number of attendees",
)
@click.option("--notes", "-txt", help="Notes.")
@requires_auth
@requires_permissions(["create_event"])
def create_event(
    contract_id: int,
    event_name: str,
    start: str,
    end: str,
    address: str,
    city: str,
    country: str,
    postal: str,
    attendees: int,
    notes: str,
) -> None:
    """Create an event and add it to the database."""
    try:
        controller.events.create(
            name=event_name,
            start_date=start,
            end_date=end,
            address_line=address,
            city=city,
            country=country,
            postal_code=postal,
            attendees_number=attendees,
            contract_id=contract_id,
            notes=notes,
        )
        click.echo("Event created.")
    except Exception as e:
        click.echo(f"Error: {e}")


@eecrm.command(name="update-event", short_help="Update an event.")
@click.argument("event_id", type=int)
@click.option("--name", "-n", help="New event name.")
@click.option("--start", "-s", help="New start date and time (YYYY-MM-DD HH:MM).")
@click.option("--end", "-e", help="New end date and time (YYYY-MM-DD HH:MM).")
@click.option("--address", "-a", help="New address line.")
@click.option("--city", "-c", help="New city.")
@click.option("--country", "-C", help="New country.")
@click.option("--postal", "-p", help="New postal code.")
@click.option("--attendees", "-nb", type=int, help="New number of attendees.")
@click.option("--notes", "-txt", help="New notes.")
@click.option("--append", "-ap", is_flag=True, help="Append notes.")
@click.option("--support_id", "-sid", type=int, help="Support person id.")
@requires_auth
@requires_permissions(["update_event"])
def update_event(
    event_id: int,
    name: str,
    start: str,
    end: str,
    address: str,
    city: str,
    country: str,
    postal: str,
    attendees: int,
    notes: str,
    append: bool,
    support_id: int,
) -> None:
    """Update an event's details."""
    try:
        controller.events.update(
            event_id=event_id,
            name=name,
            start_date=start,
            end_date=end,
            address_line=address,
            city=city,
            country=country,
            postal_code=postal,
            attendees_number=attendees,
            notes=notes,
            append=append,
            support_person_id=support_id,
        )
        click.echo("Event updated.")
    except Exception as e:
        click.echo(f"Error: {e}")


@eecrm.command(name="list-events", short_help="List events.")
@click.option("--nosupport", "-ns", is_flag=True, help="List events without support.")
@click.option(
    "--mine", "-m", is_flag=True, help="List events assigned to current user."
)
@requires_auth
def list_events(nosupport, mine):
    """
    List events. With --nosupport, list events without support person.
    With --mine, list events assigned to current user.
    """
    if nosupport:
        try:
            events = controller.events.get_events_without_support()
            view.event.display_events(events)
        except Exception as e:
            click.echo(f"Error: {e}")
    elif mine:
        try:
            events = controller.events.get_events_assigned_to_current_user()
            view.event.display_events(events)
        except Exception as e:
            click.echo(f"Error: {e}")
    else:
        try:
            events = controller.events.get_all()
            view.event.display_events(events)
        except Exception as e:
            click.echo(f"Error: {e}")


if __name__ == "__main__":
    eecrm()
