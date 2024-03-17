from epic_events_crm.database import get_session
from epic_events_crm.controllers.employees import EmployeeController
from epic_events_crm.controllers.clients import ClientController
from epic_events_crm.controllers.contracts import ContractController
from epic_events_crm.controllers.events import EventController


class MainController:
    """
    Main controller class.
    If no session is provided to constructor, a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()
        self.employees = EmployeeController(self.session)
        self.clients = ClientController(self.session)
        self.contracts = ContractController(self.session)
        self.events = EventController(self.session)
