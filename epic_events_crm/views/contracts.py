from typing import List, TYPE_CHECKING
from rich.table import Table

from epic_events_crm.views.console import console

if TYPE_CHECKING:
    from epic_events_crm.models.contracts import Contract


class ContractView:
    """Contract related views"""

    def __init__(self):
        self.console = console

    def display_contracts(self, contracts: List["Contract"]) -> None:
        """Display a list of contracts"""
        if not contracts:
            self.console.print("No contracts found.", style="bold yellow")
            return

        # Create a table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            style="on blue",
            title="CONTRACTS",
            title_style="bold white",
        )
        table.add_column("ID")
        table.add_column("Client Name (ID)")
        table.add_column("Price (EUR)")
        table.add_column("Due (EUR)")
        table.add_column("Signed")
        table.add_column("Event name (ID)")
        # Add rows to the table
        for contract in contracts:
            client_info = (
                f"{contract.client.fname} {contract.client.lname} "
                f"({contract.client_id})"
            )
            event_info = (
                f"{contract.event.name} ({contract.event.id})" if contract.event else ""
            )
            table.add_row(
                str(contract.id),
                str(client_info),
                str(contract.total_amount),
                str(contract.due_amount),
                str(contract.signed),
                str(event_info),
            )

        self.console.print(table)
