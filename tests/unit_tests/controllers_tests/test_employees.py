import importlib
import pytest
from sqlalchemy import inspect, exc

from epic_events_crm.models.employees import Employee
from epic_events_crm.controllers.employees import EmployeeController

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

    @pytest.fixture(autouse=True)
    def setup_class(self, session):
        self.controller = EmployeeController(session)
        self.employee1_kwargs = {
            "fname": "John",
            "lname": "Doe",
            "email": "johndoe@test.com",
            "password": "Passw0rd",
            "department_id": "1",
        }
        self.employee2_kwargs = {
            "fname": "Jane",
            "lname": "Doe",
            "email": "janedoe@test.fr",
            "password": "Passw0rd",
            "department_id": "1",
        }

    def test_add(self):
        """Test that the employee is added to the session."""
        employee1 = Employee(**self.employee1_kwargs)
        employee2 = Employee(**self.employee2_kwargs)
        self.controller.add(employee1)
        assert inspect(employee1).pending
        self.controller.session.flush()
        assert inspect(employee1).persistent
        self.controller.add(employee2)
        assert inspect(employee2).pending

    def test_get_by_email(self):
        """Test that an employee is obtained by its email with expected attributes."""
        employee = self.controller.get_by_email("janedoe@test.fr")
        assert isinstance(employee, Employee)
        assert inspect(employee).persistent
        assert employee.fname == "Jane" and employee.lname == "Doe"
        assert employee.password.startswith("$argon2id$")
        assert employee.created_at is not None

    def test_get_by_id(self):
        """Test that an employee is obtained by its id."""
        employee = self.controller.get_by_id(8)
        assert isinstance(employee, Employee)

    def test_get_all(self):
        """Test the method returns all employees as an Employee list."""
        employees = self.controller.get_all()
        assert isinstance(employees, list)
        assert isinstance(employees[0], Employee)

    def test_delete(self):
        """Test that an employee is marked for deletion in the session."""
        employee = self.controller.get_by_email("janedoe@test.fr")
        self.controller.delete(employee)
        self.controller.session.flush()  # else it'd be still persistent
        assert inspect(employee).deleted

    def test_add_existing_email(self):
        """Test add method with an existing email."""
        employee = Employee(**self.employee1_kwargs)
        self.controller.add(employee)
        with pytest.raises(exc.IntegrityError):
            self.controller.session.flush()
