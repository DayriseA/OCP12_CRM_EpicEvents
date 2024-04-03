import pytest
from sqlalchemy import inspect, exc

from epic_events_crm.models.clients import Client
from epic_events_crm.repositories.clients import ClientRepo


class TestClientRepo:
    """Test ClientRepo class."""

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup(cls, session):
        cls.repo = ClientRepo(session)
        cls.client1_kwargs = {
            "fname": "Sung",
            "lname": "JINWOO",
            "email": "sungjinwoo@test.com",
            "phone": "0262123456",
            "company_name": "Solo Leveling",
            "salesperson_id": "5",
        }
        # email not unique case
        cls.client2_kwargs = {
            "fname": "Sung",
            "lname": "JIN",
            "email": "sungjinwoo@test.com",
            "salesperson_id": "5",
        }
        # phone not unique case
        cls.client3_kwargs = {
            "fname": "Sung",
            "lname": "WOO",
            "email": "sungjinwoo@mail.com",
            "phone": "0262123456",
            "salesperson_id": "5",
        }

    def test_add(self):
        """Test that the client is added to the session."""
        client1 = Client(**self.client1_kwargs)
        self.repo.add(client1)
        assert inspect(client1).pending
        self.repo.session.commit()
        assert inspect(client1).persistent

    def test_get_by_email(self):
        """Test that the right client is obtained by its email."""
        client = self.repo.get_by_email("sungjinwoo@test.com")
        assert isinstance(client, Client)
        assert client.fname == "Sung" and client.lname == "JINWOO"
        assert client.email == "sungjinwoo@test.com"
        assert client.phone == "0262123456"
        assert client.company_name == "Solo Leveling"
        assert client.salesperson_id == 5
        assert client.created_at is not None

    def test_get_by_phone(self):
        """Test that the right client is obtained by its phone."""
        client = self.repo.get_by_phone("0262123456")
        assert isinstance(client, Client)
        assert client.fname == "Sung" and client.lname == "JINWOO"
        assert client.email == "sungjinwoo@test.com"
        assert client.phone == "0262123456"

    def test_get_by_id(self):
        """Test that the right client is obtained by its id"""
        client = self.repo.get_by_id(1)  # from conftest.py 'populate_db' fixture
        assert isinstance(client, Client)
        assert client.email == "jdoe@mail.com"

    def test_get_all(self):
        """Test that all clients are obtained as a list of Client objects."""
        clients = self.repo.get_all()
        assert isinstance(clients, list)
        assert all(isinstance(client, Client) for client in clients)

    def test_add_existing_email(self):
        """Test that adding a client with an existing email raises an error."""
        client2 = Client(**self.client2_kwargs)
        self.repo.add(client2)
        with pytest.raises(exc.IntegrityError):
            self.repo.session.flush()
        self.repo.session.rollback()  # avoid PendingRollbackError

    def test_add_existing_phone(self):
        """Test that adding a client with an existing phone raises an error."""
        client3 = Client(**self.client3_kwargs)
        self.repo.add(client3)
        with pytest.raises(exc.IntegrityError):
            self.repo.session.flush()
        self.repo.session.rollback()

    def test_delete(self):
        """Test that a client is marked for deletion in the session."""
        client = self.repo.get_by_email("sungjinwoo@test.com")
        self.repo.delete(client)
        self.repo.session.flush()  # else it'd be still persistent
        assert inspect(client).deleted

    def test_get_clients_assigned_to_a_salesperson(self):
        """Test that all clients assigned to a salesperson are obtained."""
        clients = self.repo.get_clients_assigned_to(4)
        expected_clients_emails = ["jdoe@mail.com", "jdae@mail.com", "gsophie@mail.com"]
        for client in clients:
            assert client.email in expected_clients_emails
