from typing import List, TYPE_CHECKING
from rich.table import Table

from epic_events_crm.views.console import console

if TYPE_CHECKING:
    from epic_events_crm.models.events import Event


class EventView:
    """Event related views"""

    def __init__(self):
        self.console = console

    def display_events(self, events: List["Event"]) -> None:
        """Display a list of events"""
        if not events:
            self.console.print("No events found.", style="bold yellow")
            return

        # Create a table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            style="on blue",
            title="EVENTS",
            title_style="bold white",
        )
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Start", width=10)
        table.add_column("End", width=10)
        table.add_column("Address")
        table.add_column("Guests", width=6)
        table.add_column("Contract ID", width=8)
        table.add_column("Support Person (ID)")
        # Add rows to the table
        for event in events:
            address = (
                f"{event.address_line1}, \n"
                f"{event.postal_code} {event.city}\n {event.country}"
            )
            support_person_info = (
                f"{event.support_person.fname} {event.support_person.lname} "
                f"({event.support_person_id})"
                if event.support_person
                else ""
            )
            table.add_row(
                str(event.id),
                event.name,
                str(event.start_datetime),
                str(event.end_datetime),
                address,
                str(event.attendees_number),
                str(event.contract_id),
                support_person_info,
            )

        self.console.print(table)
