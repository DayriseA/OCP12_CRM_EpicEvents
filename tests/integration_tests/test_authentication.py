import importlib
import pytest
import os
import jwt
from sqlalchemy import inspect

from epic_events_crm.models.employees import Employee
from epic_events_crm.repositories.employees import EmployeeRepo
from epic_events_crm.authentication import authenticate, make_jwt_token

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


class TestAuthentication:
    """Integration tests related to authentication, login, logout, ..."""

    @pytest.fixture(autouse=True)
    def setup_class(self, session):
        self.controller = EmployeeRepo(session)
        self.employee = Employee(
            fname="John",
            lname="Doe",
            email="johndoe@email.test",
            password="Passw0rd",
            department_id=1,
        )

    def test_login_process(self, mocker):
        """Test the login process."""
        # Add the employee for the test
        self.controller.add(self.employee)
        self.controller.session.flush()
        assert inspect(self.employee).persistent
        # Authenticate the employee
        assert authenticate("johndoe@email.test", "Passw0rd", self.controller)
        # Mock get_jwt_secret to get a fixed secret
        fixed_secret = "jwt_test_secret"
        mocker.patch(
            "epic_events_crm.authentication.get_jwt_secret",
            return_value=fixed_secret,
        )
        # Create the token and decode it
        token = make_jwt_token(self.employee)
        decoded_token = jwt.decode(token, fixed_secret, algorithms=["HS256"])
        assert decoded_token["uid"] == self.employee.id
        assert decoded_token["department_id"] == self.employee.department_id
        os.environ["JWT_TEST_TOKEN"] = token
        assert os.getenv("JWT_TEST_TOKEN") == token
