import getpass


class BaseView:
    """Basic views for the CRM app."""

    def display_msg(self, msg: str) -> None:
        """Display a message."""
        # to be changed later with use of click and rich
        print(msg)

    def ask_app_key(self) -> str:
        """Ask for the app key."""
        return getpass.getpass("Please enter the application key: ")
