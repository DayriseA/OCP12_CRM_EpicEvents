import importlib
import pytest
from sqlalchemy import inspect, exc

from epic_events_crm.models.departments_permissions import Department
from epic_events_crm.controllers.departments_permissions import DepartmentController

NEEDED_MODULES = (
    "epic_events_crm.models.departments_permissions",
    "epic_events_crm.models.clients",
    "epic_events_crm.models.contracts",
    "epic_events_crm.models.events",
    "epic_events_crm.models.employees",
)
for module in NEEDED_MODULES:
    try:
        importlib.import_module(module)
    except Exception as e:
        print(f"Could not import module {module}.")
        print(f"Error: {e}")


class TestDepartmentController:
    """Test DepartmentController class."""

    @pytest.fixture(autouse=True)
    def setup_class(self, session):
        self.controller = DepartmentController(session)

    def test_add(self):
        """Test that the department is added to the session."""
        department = Department(name="Sales_test")
        department_2 = Department(name="Support_test")
        self.controller.add(department)
        assert inspect(department).pending
        self.controller.session.flush()
        assert inspect(department).persistent
        self.controller.add(department_2)
        assert inspect(department_2).pending

    def test_get_by_name(self):
        """Test that a department is obtained by its name."""
        department = self.controller.get_by_name("Support_test")
        assert isinstance(department, Department)
        assert department.name == "Support_test"

        # as a side effect the query changed the state from pending to persistent
        assert inspect(department).persistent

    def test_get_by_id(self):
        """Test that a department is obtained by its id."""
        department = self.controller.get_by_id(1)
        assert isinstance(department, Department)

    def test_get_all(self):
        """Test the method returns all departments as a Department list."""
        departments = self.controller.get_all()
        assert isinstance(departments, list)
        assert isinstance(departments[0], Department)

    def test_delete(self):
        """Test that a department is marked for deletion in the session."""
        department = self.controller.get_by_name("Support_test")
        self.controller.delete(department)
        # from epic_events_crm.database import get_state_name
        # state_name = get_state_name(department)
        # print(f"Department state: {state_name}")
        # we have to flush else its still shows as persistent
        self.controller.session.flush()
        assert inspect(department).deleted

    def test_add_existing_name(self):
        """Test add method with an existing name."""
        department = Department(name="Sales_test")
        self.controller.add(department)  # No error because it's still pending
        with pytest.raises(exc.IntegrityError):
            self.controller.session.flush()
