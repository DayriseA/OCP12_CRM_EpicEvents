import getpass

from epic_events_crm.views.console import console


class BaseView:
    """Basic views for the CRM app."""

    def __init__(self):
        self.console = console

    def display_msg(self, msg: str) -> None:
        """Display a message."""
        self.console.print(msg)

    def ask_app_key(self) -> str:
        """Ask for the app key."""
        return getpass.getpass("Please enter the application key: ")

    def display_as(self, msg: str, level: str) -> None:
        """Display a message with a specific style depending on the level."""
        if level == "info":
            self.console.print(msg, style="bold green")
        elif level == "warning":
            self.console.print(msg, style="bold gold1")
        elif level == "error":
            self.console.print(msg, style="bold red")
        else:
            self.console.print(msg)
