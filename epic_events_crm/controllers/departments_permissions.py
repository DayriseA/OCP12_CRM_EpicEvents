from epic_events_crm.database import get_session
from epic_events_crm.repositories.departments_permissions import DepartmentRepo


class DepartmentController:
    """
    Department controller class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()
        self.repo = DepartmentRepo(self.session)

    def display_all(self) -> str:
        """List all departments and their id."""
        departments = self.repo.get_all()
        msg = "Availables departments:\n"
        for department in departments:
            msg += f"{department.name.upper()} (id:{department.id})\n"
        return msg
