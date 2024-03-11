import importlib

# import pytest
# from sqlalchemy import inspect, exc

# from epic_events_crm.models.employees import Employee
# from epic_events_crm.controllers.employees import EmployeeController

NEEDED_MODULES = (
    "epic_events_crm.models.departments_permissions",
    "epic_events_crm.models.clients",
    "epic_events_crm.models.contracts",
    "epic_events_crm.models.events",
)
for module in NEEDED_MODULES:
    try:
        importlib.import_module(module)
    except Exception as e:
        print(f"Could not import module {module}.")
        print(f"Error: {e}")


class TestEmployeeController:
    """Test EmployeeController class."""

    pass
