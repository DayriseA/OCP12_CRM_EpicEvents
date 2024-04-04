import pytest
from typing import Optional

from epic_events_crm.models.clients import Client
from epic_events_crm.controllers.clients import ClientController
from epic_events_crm.authentication import log_in, valid_token_in_env
from epic_events_crm.models.employees import Employee
from epic_events_crm.repositories.employees import EmployeeRepo

c_invalid_email_kwargs = {
    "fname": "Invalid",
    "lname": "Email",
    "email": "invalidemail",
    "salesperson_id": 5,
}
c_used_email_kwargs = {
    "fname": "Used",
    "lname": "Email",
    "email": "gsophie@mail.com",
    "salesperson_id": 5,
}
c_invalid_phone_kwargs = {
    "fname": "Invalid",
    "lname": "Phone",
    "email": "invalidphone@test.com",
    "salesperson_id": 5,
    "phone": "123456",
}
c_used_phone_kwargs = {
    "fname": "Used",
    "lname": "Phone",
    "email": "usedphone@test.com",
    "salesperson_id": 5,
    "phone": "0123456789",
}
c_valid_kwargs = {
    "fname": "vaLId",
    "lname": "cLiEnt",
    "email": "vclient@test.com",
    "salesperson_id": 5,
    "phone": "9876543210",
    "company_name": "Valid Company",
}
u_no_identifiers_kwargs = {"fname": "Updated", "lname": "Client"}
u_unknown_id_kwargs = {"client_id": 999, "fname": "Updated", "lname": "Client"}
u_unknown_email_kwargs = {"email": "unknown@test.com", "fname": "Updated"}
u_id_ok_invalid_email_kwargs = {"client_id": 1, "email": "invalidemail"}
u_id_ok_used_email_kwargs = {"client_id": 1, "email": "blyah@mail.com"}
u_not_assigned_to_client_kwargs = {"client_id": 1, "company_name": "Updated Company"}
u_unknown_salesperson_kwargs = {"email": "vclient@test.com", "salesperson_id": 999}
u_not_a_salesperson_kwargs = {"email": "vclient@test.com", "salesperson_id": 3}
u_invalid_phone_kwargs = {"email": "vclient@test.com", "phone": "0245 4"}
u_used_phone_kwargs = {"email": "vclient@test.com", "phone": "0123456789"}


class TestClientController:
    """
    Test ClientController class.
    Take into account the 'populate_db' fixture from conftest.py.
    """

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup(cls, session):
        cls.controller = ClientController(session)
        cls.employee_repo = EmployeeRepo(session)

    def test_create(self):
        """Test that the client is created and added to the database."""
        self.controller.create(**c_valid_kwargs)
        # check that the client is in the database
        client = self.controller.repo.get_by_email("vclient@test.com")
        # title() and upper() are used in the controller
        assert client.fname == "Valid" and client.lname == "CLIENT"

    @pytest.mark.parametrize(
        "client_kwargs, expected",
        [
            (c_invalid_email_kwargs, ValueError),
            (c_used_email_kwargs, ValueError),
            (c_invalid_phone_kwargs, ValueError),
            (c_used_phone_kwargs, ValueError),
        ],
    )
    def test_create_raises_errors(self, client_kwargs, expected):
        """Test that the create method raises the expected errors."""
        with pytest.raises(expected):
            self.controller.create(**client_kwargs)

    # We need to change the get_current_user method called in the update method so that
    # its tied to the test database and not the actual database
    def get_current_user_test(self) -> Optional[Employee]:
        """Return current user from .env JWT token. Runs against the test database."""
        token = valid_token_in_env()
        if token:
            return self.employee_repo.get_by_id(token["uid"])
        return None

    @pytest.mark.parametrize(
        "client_kwargs, expected",
        [
            (u_no_identifiers_kwargs, ValueError),
            (u_unknown_id_kwargs, ValueError),
            (u_unknown_email_kwargs, ValueError),
            (u_id_ok_invalid_email_kwargs, ValueError),
            (u_id_ok_used_email_kwargs, ValueError),
            (u_not_assigned_to_client_kwargs, PermissionError),
            (u_unknown_salesperson_kwargs, ValueError),
            (u_not_a_salesperson_kwargs, ValueError),
            (u_invalid_phone_kwargs, ValueError),
            (u_used_phone_kwargs, ValueError),
        ],
    )
    def test_update_raises_errors(self, mocker, client_kwargs, expected):
        """Test that the update method raises the expected errors."""
        # some update logic depends on the current user
        log_in("dvalentin@sales.com", "Passw0rd", self.employee_repo)
        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.clients.get_current_user",
            new=self.get_current_user_test,
        )
        with pytest.raises(expected):
            self.controller.update(**client_kwargs)

    def test_update(self, mocker):
        """Test that the client is updated in the database."""
        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.clients.get_current_user",
            new=self.get_current_user_test,
        )
        # Already logged (dvalentin@sales.com) as the assigned salesperson
        self.controller.update(
            client_id=5,
            fname="updated",
            lname="updated",
            email="updated@test.com",
            salesperson_id=4,
            phone="1234 777 888",
            company_name="Updated Company",
        )
        # check the updates
        client = self.controller.repo.get_by_id(5)
        assert client.fname == "Updated"
        assert client.lname == "UPDATED"
        assert client.email == "updated@test.com"
        assert client.salesperson_id == 4
        assert client.phone == "1234777888"
        assert client.company_name == "Updated Company"

    def test_delete(self):
        """Test that the client is deleted from the database."""
        client = self.controller.repo.get_by_id(5)
        self.controller.delete(client)
        assert self.controller.repo.get_by_id(5) is None

    def test_get_all(self):
        """Test that all clients are obtained as a list of Client objects."""
        clients = self.controller.get_all()
        assert len(clients) == 4
        assert all(isinstance(client, Client) for client in clients)

    def test_get_clients_assigned_to_current_user(self, mocker):
        """Test that all clients assigned to the current user are obtained."""
        log_in("aquentin@sales.com", "Passw0rd", self.employee_repo)
        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.clients.get_current_user",
            new=self.get_current_user_test,
        )
        clients = self.controller.get_clients_assigned_to_current_user()
        assert len(clients) == 3
        assert all(client.salesperson_id == 4 for client in clients)
