import pytest
from dotenv import set_key

from epic_events_crm.models.employees import Employee
from epic_events_crm.repositories.employees import EmployeeRepo
from epic_events_crm.authentication import (
    log_in,
    valid_token_in_env,
    get_current_user,
    requires_auth,
)


@requires_auth
def some_function():
    return "Hello world!"


class TestAuthentication:
    """
    Integration tests related to authentication, login, logout, ...
    Take into account the 'populate_db' fixture from conftest.py.
    """

    @pytest.fixture(autouse=True, scope="class")
    def setup_class(self, session):
        self.__class__.repo = EmployeeRepo(session)

    def test_login_process(self):
        """Test the login process."""
        # reset the token in the .env file
        set_key(".env", "JWT_TOKEN", "")
        # @requires_auth decorator prevents the function from running
        result = some_function()
        assert result is None
        # wrong password or email returns False
        assert log_in("aquentin@sales.com", "wrongpassword", self.repo) is False
        assert log_in("aquenin@sales.com", "Passw0rd", self.repo) is False
        # correct email and password returns True
        assert log_in("aquentin@sales.com", "Passw0rd", self.repo) is True
        assert valid_token_in_env() is not False
        # get the user from the token
        user = get_current_user(self.repo)
        assert isinstance(user, Employee)
        assert user.email == "aquentin@sales.com"
        # the function can now run
        result = some_function()
        assert result == "Hello world!"
