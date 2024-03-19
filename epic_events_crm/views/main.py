from epic_events_crm.views.base import BaseView
from epic_events_crm.views.employees import EmployeeView
from epic_events_crm.views.clients import ClientView
from epic_events_crm.views.contracts import ContractView
from epic_events_crm.views.events import EventView


class MainView:
    """Main view class"""

    def __init__(self):
        self.base = BaseView()
        self.employee = EmployeeView()
        self.client = ClientView()
        self.contract = ContractView()
        self.event = EventView()
