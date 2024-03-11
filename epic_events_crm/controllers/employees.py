from epic_events_crm.database import get_session
from epic_events_crm.repositories.employees import EmployeeRepo


class EmployeeController:
    """
    Employee controller class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()
        self.repo = EmployeeRepo(self.session)

    pass
