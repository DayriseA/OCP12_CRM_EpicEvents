import pytest

from epic_events_crm.models.employees import Employee
from epic_events_crm.controllers.employees import EmployeeController

superuser_kwargs = {
    "fname": "Super",
    "lname": "User",
    "email": "superuser@test.com",
    "password": "Passw0rd",
    "department_id": 1,
}
invalid_email_kwargs = {
    "fname": "Invalid",
    "lname": "Email",
    "email": "invalid@email",
    "password": "Passw0rd",
    "department_id": 2,
}
used_email_kwargs = {
    "fname": "Used",
    "lname": "Email",
    "email": "hsabrina@manager.com",
    "password": "Passw0rd",
    "department_id": 2,
}
invalid_department_kwargs = {
    "fname": "Invalid",
    "lname": "Department",
    "email": "invaliddepartment@test.com",
    "password": "Passw0rd",
    "department_id": 999,
}


class TestEmployeeController:
    """
    Test EmployeeController class.
    Take into account the 'populate_db' fixture from conftest.py.
    """

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup(cls, session):
        cls.controller = EmployeeController(session)

    def test_create(self):
        """Test that the create method works as expected."""
        # define valid arguments
        fname = "Valid"
        lname = "Employee"
        email = "validemp@test.com"
        password = "Passw0rd"
        department_id = 2
        # call the method
        self.controller.create(
            fname=fname,
            lname=lname,
            email=email,
            password=password,
            department_id=department_id,
        )
        # check the result (supposed to be in the database with id=8)
        employee = self.controller.repo.get_by_id(8)
        assert employee.email == email

    @pytest.mark.parametrize(
        "user_kwargs, expected",
        [
            (superuser_kwargs, PermissionError),
            (invalid_email_kwargs, ValueError),
            (used_email_kwargs, ValueError),
            (invalid_department_kwargs, ValueError),
        ],
    )
    def test_create_raises_errors(self, user_kwargs, expected):
        """Test that the create method works as expected with wrong parameters."""
        with pytest.raises(expected):
            self.controller.create(**user_kwargs)
            self.controller.session.rollback()

    def test_update_with_wrong_arguments(self):
        """Test that the expected errors are raised with invalid arguments."""
        # no identifier (id or mail) provided
        with pytest.raises(ValueError):
            self.controller.update(fname="John", lname="Doe")

        # non-existing employee id
        with pytest.raises(ValueError):
            self.controller.update(employee_id=999, fname="John", lname="Doe")

        # valid id but invalid email
        with pytest.raises(ValueError):
            self.controller.update(employee_id=8, email="invalidemail")

        # valid id but used email
        with pytest.raises(ValueError):
            self.controller.update(employee_id=8, email="pmercedes@supp.com")

        # non-existing email
        with pytest.raises(ValueError):
            self.controller.update(email="dlsjfdlf@test.fr", fname="John", lname="Doe")

        # valid identifier but invalid department id
        with pytest.raises(ValueError):
            self.controller.update(email="validemp@test.com", department_id=999)

        self.controller.session.rollback()

    def test_update(self):
        """Test that the update method works as expected."""
        self.controller.update(
            employee_id=8, email="updated@test.com", fname="Updated", department_id=3
        )
        employee = self.controller.repo.get_by_id(8)
        assert employee.email == "updated@test.com"
        assert employee.fname == "Updated"
        assert employee.lname == "EMPLOYEE"
        assert employee.department_id == 3

    def test_delete(self):
        """Test that the delete method removes the employee from the database."""
        employee = self.controller.repo.get_by_id(8)
        self.controller.delete(employee)
        assert self.controller.repo.get_by_id(8) is None

    def test_get_all(self):
        """Test that the get_all method returns all employees."""
        employees = self.controller.get_all()
        assert len(employees) == 7
        assert all(isinstance(employee, Employee) for employee in employees)

    def test_create_superuser(self):
        """Test that the create_superuser method works as expected."""
        self.controller.create_superuser(
            fname="Super", lname="User", email="superuser@test.com", password="Passw0rd"
        )
        employee = self.controller.repo.get_by_email("superuser@test.com")
        assert employee.fname == "Super"
        assert employee.department_id == 1
