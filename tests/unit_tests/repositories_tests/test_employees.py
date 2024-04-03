import pytest
from sqlalchemy import inspect, exc

from epic_events_crm.models.employees import Employee
from epic_events_crm.repositories.employees import EmployeeRepo


class TestEmployeeRepo:
    """Test EmployeeRepo class."""

    # https://stackoverflow.com/questions/62289556/pytest-fixture-with-scope-class-doesnt-works-with-setup-class-method
    # https://stackoverflow.com/questions/63552491/pytest-assigning-attribute-in-a-fixture-not-visible-to-test-cases
    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup(cls, session):
        cls.repo = EmployeeRepo(session)
        cls.employee1_kwargs = {
            "fname": "Jean",
            "lname": "DUH",
            "email": "jeanduh@test.com",
            "password": "Passw0rd",
            "department_id": "1",
        }
        cls.employee2_kwargs = {
            "fname": "Jane",
            "lname": "DOE",
            "email": "janedoe@test.fr",
            "password": "Passw0rd",
            "department_id": "1",
        }

    def test_setup(self):
        """Test the setup."""
        assert self.repo.session is not None
        assert self.employee1_kwargs is not None
        assert self.employee2_kwargs is not None

    def test_add(self):
        """Test that the employee is added to the session."""
        employee1 = Employee(**self.employee1_kwargs)
        employee2 = Employee(**self.employee2_kwargs)
        self.repo.add(employee1)
        assert inspect(employee1).pending
        self.repo.session.commit()
        assert inspect(employee1).persistent
        self.repo.add(employee2)
        assert inspect(employee2).pending

    def test_get_by_email(self):
        """Test that an employee is obtained by its email with expected attributes."""
        employee = self.repo.get_by_email("jeanduh@test.com")
        assert isinstance(employee, Employee)
        assert employee.fname == "Jean" and employee.lname == "DUH"
        assert employee.email == "jeanduh@test.com"
        assert employee.password.startswith("$argon2id$")
        assert employee.created_at is not None

    def test_get_by_id(self):
        """Test that an employee is obtained by its id."""
        employee = self.repo.get_by_id(2)  # from conftest.py 'populate_db' fixture
        assert isinstance(employee, Employee)
        assert employee.email == "flionel@manager.com"

    def test_get_all(self):
        """Test the method returns all employees as an Employee list."""
        employees = self.repo.get_all()
        assert isinstance(employees, list)
        assert all(isinstance(employee, Employee) for employee in employees)

    def test_delete(self):
        """Test that an employee is marked for deletion in the session."""
        employee = self.repo.get_by_email("janedoe@test.fr")
        self.repo.delete(employee)
        self.repo.session.flush()  # else it'd be still persistent
        assert inspect(employee).deleted

    def test_add_existing_email(self):
        """Test add method with an existing email."""
        employee = Employee(**self.employee1_kwargs)
        self.repo.add(employee)
        with pytest.raises(exc.IntegrityError):
            self.repo.session.flush()
