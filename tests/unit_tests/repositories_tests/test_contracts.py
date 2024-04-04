import pytest
from sqlalchemy import inspect, exc

from epic_events_crm.models.contracts import Contract
from epic_events_crm.repositories.contracts import ContractRepo

CREATED_ID = None


class TestContractRepo:
    """
    Test ContractRepo class.
    Take into account the 'populate_db' fixture from conftest.py.
    """

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup(cls, session):
        cls.repo = ContractRepo(session)
        cls.contract1_kwargs = {
            "client_id": "1",
            "total_amount": "1000",
            "due_amount": "500",
        }
        # client_id not existing case
        cls.contract2_kwargs = {
            "client_id": "888",
            "total_amount": "1000",
            "due_amount": "1000",
        }

    def test_add(self):
        """Test that the contract is added to the session."""
        contract1 = Contract(**self.contract1_kwargs)
        self.repo.add(contract1)
        assert inspect(contract1).pending
        self.repo.session.commit()
        assert inspect(contract1).persistent
        global CREATED_ID
        CREATED_ID = contract1.id

    def test_add_non_existing_client(self):
        """Adding a contract with a non-existing client should raise an error."""
        contract2 = Contract(**self.contract2_kwargs)
        self.repo.add(contract2)
        with pytest.raises(exc.IntegrityError):
            self.repo.session.flush()
        self.repo.session.rollback()

    def test_get_by_id(self):
        """Test that a contract can be retrieved by its id."""
        contract = self.repo.get_by_id(1)
        assert isinstance(contract, Contract)
        assert contract.id == 1

    def test_get_all(self):
        """Test that all contracts are retrieved as a list of Contract objects."""
        contracts = self.repo.get_all()
        assert isinstance(contracts, list)
        assert all(isinstance(contract, Contract) for contract in contracts)

    def test_get_unsigned(self):
        """Test that all unsigned contracts are retrieved."""
        unsigned_contracts = self.repo.get_unsigned()
        assert isinstance(unsigned_contracts, list)
        assert all(not contract.signed for contract in unsigned_contracts)
        assert len(unsigned_contracts) == 4

    def test_get_unpaid(self):
        """Test that all unpaid contracts are retrieved."""
        unpaid_contracts = self.repo.get_unpaid()
        assert isinstance(unpaid_contracts, list)
        assert all(contract.due_amount > 0 for contract in unpaid_contracts)
        assert len(unpaid_contracts) == 6

    def test_get_unsigned_or_unpaid(self):
        """Test that all unsigned or unpaid contracts are retrieved."""
        unsigned_or_unpaid_contracts = self.repo.get_unsigned_or_unpaid()
        assert isinstance(unsigned_or_unpaid_contracts, list)
        assert all(
            not contract.signed or contract.due_amount > 0
            for contract in unsigned_or_unpaid_contracts
        )
        assert len(unsigned_or_unpaid_contracts) == 6

    def test_get_by_salesperson(self):
        """Test that all contracts related to a salesperson are retrieved."""
        contracts = self.repo.get_by_salesperson(5)
        assert isinstance(contracts, list)
        assert all(contract.client.salesperson_id == 5 for contract in contracts)
        assert len(contracts) == 2

    def test_get_without_event(self):
        """Test that all contracts without an event are retrieved."""
        contracts = self.repo.get_without_event()
        assert isinstance(contracts, list)
        assert all(contract.event is None for contract in contracts)
        assert len(contracts) == 4

    def test_get_by_salesperson_and_wo_event(self):
        """
        Test that all contracts without an event
        and related to a salesperson are retrieved.
        """
        contracts = self.repo.get_by_salesperson_and_wo_event(4)
        assert isinstance(contracts, list)
        assert all(
            contract.client.salesperson_id == 4 and contract.event is None
            for contract in contracts
        )
        assert len(contracts) == 4

    def test_delete(self):
        """Test that a contract is marked for deletion in the session."""
        contract = self.repo.get_by_id(CREATED_ID)  # the one created in this test class
        self.repo.delete(contract)
        self.repo.session.flush()
        assert inspect(contract).deleted
