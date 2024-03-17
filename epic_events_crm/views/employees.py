from typing import List, TYPE_CHECKING
from rich.table import Table

from epic_events_crm.views.console import console

if TYPE_CHECKING:
    from epic_events_crm.models.employees import Employee


class EmployeeView:
    """Employee related views"""

    def __init__(self):
        self.console = console

    def display_employees(self, employees: List["Employee"]) -> None:
        """Display a list of employees"""
        if not employees:
            self.console.print("No employees found.", style="bold yellow")
            return

        # Create a table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            style="on blue",
            title="EMPLOYEES",
            title_style="bold white",
        )
        table.add_column("ID")
        table.add_column("Firstname")
        table.add_column("Lastname")
        table.add_column("Email")
        table.add_column("Department (ID)")
        # Add rows to the table
        for employee in employees:
            table.add_row(
                str(employee.id),
                employee.fname,
                employee.lname,
                employee.email,
                f"{employee.department.name} ({employee.department.id})",
            )

        self.console.print(table)
