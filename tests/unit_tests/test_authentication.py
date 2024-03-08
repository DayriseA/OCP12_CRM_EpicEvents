import datetime
import jwt
import pytest

from epic_events_crm.models.employees import Employee
from epic_events_crm.controllers.employees import EmployeeController
from epic_events_crm.authentication import authenticate, make_jwt_token


class TestAuthentication:
    """Tests related to authentication, login, logout, ..."""

    @pytest.mark.parametrize(
        "email, password, expected",
        [
            ("existing@email.test", "correct_pwd", True),
            ("existing@email.test", "wrong_pwd", False),
            ("nonexistent@email.test", "any_pwd", False),
        ],
    )
    def test_authenticate(self, mocker, email, password, expected):
        """Test the authenticate function."""
        # Mock the get_by_email method
        mocker.patch.object(EmployeeController, "get_by_email", return_value=None)
        if email == "existing@email.test":
            employee = mocker.Mock(spec=Employee)
            employee.check_password.return_value = password == "correct_pwd"
            mocker.patch.object(
                EmployeeController, "get_by_email", return_value=employee
            )

        result = authenticate(email, password)
        assert result == expected

    def test_make_jwt_token(self, mocker):
        """Test the make_jwt_token function."""
        # Mock an employee
        employee = mocker.Mock(spec=Employee)
        employee.id = 1
        employee.password = "hashed_password"

        # Mock get_jwt_secret to get a fixed secret
        fixed_secret = "jwt_test_secret"
        mocker.patch(
            "epic_events_crm.authentication.get_jwt_secret",
            return_value=fixed_secret,
        )

        token = make_jwt_token(employee)  # Create the token
        decoded_token = jwt.decode(token, fixed_secret, algorithms=["HS256"])

        assert decoded_token["uid"] == employee.id
        assert decoded_token["hash"] == employee.password
        # Check that the expiration token is roughly 15 minutes from now
        # 1s should be enough for any time elapsed between token creation and assertion
        expiration_datetime = datetime.datetime.fromtimestamp(decoded_token["exp"])
        time_difference = (
            datetime.datetime.now()
            + datetime.timedelta(minutes=15)
            - expiration_datetime
        )
        assert time_difference.total_seconds() < 1
