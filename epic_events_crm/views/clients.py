from typing import List, TYPE_CHECKING
from rich.table import Table

from epic_events_crm.views.console import console

if TYPE_CHECKING:
    from epic_events_crm.models.clients import Client


class ClientView:
    """Client related views"""

    def __init__(self):
        self.console = console

    def display_clients(self, clients: List["Client"]) -> None:
        """Display a list of clients"""
        if not clients:
            self.console.print("No clients found.", style="bold yellow")
            return

        # Create a table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            style="on blue",
            title="CLIENTS",
            title_style="bold white",
        )
        table.add_column("ID")
        table.add_column("Firstname")
        table.add_column("Lastname")
        table.add_column("Email")
        table.add_column("Phone")
        table.add_column("Company Name")
        table.add_column("Salesperson ID", width=5)
        # Add rows to the table
        for client in clients:
            table.add_row(
                str(client.id),
                client.fname,
                client.lname,
                client.email,
                client.phone,
                client.company_name,
                str(client.salesperson_id),
            )

        self.console.print(table)
