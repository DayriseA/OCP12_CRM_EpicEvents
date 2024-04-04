import pytest
from sqlalchemy import exc
from typing import Optional
from decimal import Decimal

from epic_events_crm.models.contracts import Contract
from epic_events_crm.controllers.contracts import ContractController
from epic_events_crm.authentication import log_in, valid_token_in_env
from epic_events_crm.models.employees import Employee
from epic_events_crm.repositories.employees import EmployeeRepo


class TestContractController:
    """
    Test ContractController class.
    Take into account the 'populate_db' fixture from conftest.py.
    """

    @pytest.fixture(scope="class", autouse=True)
    @classmethod
    def setup(cls, session):
        cls.controller = ContractController(session)
        cls.employee_repo = EmployeeRepo(session)
        cls.created_id = None

        yield
        # delete the created contract to not mess with other tests
        contract_created = cls.controller.repo.get_by_id(cls.created_id)
        cls.controller.repo.delete(contract_created)
        cls.controller.session.commit()

    def test_create_with_invalid_client_id(self):
        """Creating a contract with an invalid client_id should raise an error."""
        with pytest.raises(exc.SQLAlchemyError):
            self.controller.create(client_id=999, due_amount=1000)
        self.controller.session.rollback()  # avoid 'PendingRollbackError'

    def test_create(self):
        """Test that a contract is created for the client and added to the database."""
        created_id = self.controller.create(client_id=3, due_amount=999.99)
        # self.created_id reverts to None after if not assigned to class attribute:
        self.__class__.created_id = created_id
        contract = self.controller.repo.get_by_id(self.created_id)
        assert isinstance(contract, Contract)
        assert contract.client_id == 3
        assert contract.total_amount == Decimal("999.99")
        assert contract.due_amount == Decimal("999.99")
        assert contract.signed is False

    # We need to change the get_current_user method called in the update method so that
    # its tied to the test database and not the actual database
    def get_current_user_test(self) -> Optional[Employee]:
        """Return current user from .env JWT token. Runs against the test database."""
        token = valid_token_in_env()
        if token:
            return self.employee_repo.get_by_id(token["uid"])
        return None

    def test_update_raises_errors(self, mocker):
        """Test that the update method raises the expected errors."""
        # some update logic depends on the current user
        log_in("dvalentin@sales.com", "Passw0rd", self.employee_repo)

        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.contracts.get_current_user",
            new=self.get_current_user_test,
        )

        with pytest.raises(ValueError):
            self.controller.update(contract_id=999, total_amount=1000)
        with pytest.raises(PermissionError):
            self.controller.update(contract_id=self.created_id, total_amount=1000)
        with pytest.raises(ValueError):
            self.controller.update(contract_id=6, client_email="unknown@test.fr")

    def test_update(self, mocker):
        """Test that the update method works as expected."""
        # login with the assigned salesperson
        log_in("aquentin@sales.com", "Passw0rd", self.employee_repo)
        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.contracts.get_current_user",
            new=self.get_current_user_test,
        )

        # Get the contract for assertions
        contract = self.controller.repo.get_by_id(self.created_id)

        # Money paid implies reduction of due amount
        self.controller.update(contract_id=self.created_id, paid_amount=99.99)
        assert contract.due_amount == Decimal("900.00")

        # Update of total amount implies update of due amount
        self.controller.update(contract_id=self.created_id, total_amount=1099.99)
        assert contract.total_amount == Decimal("1099.99")
        assert contract.due_amount == Decimal("1000.00")

        # Update of signed status
        self.controller.update(contract_id=self.created_id, signed=True)
        assert contract.signed is True

        # Update of client
        self.controller.update(
            contract_id=self.created_id, client_email="jdae@mail.com"
        )
        assert contract.client_id == 2

    def test_get_all(self):
        """Test that all contracts are returned."""
        contracts = self.controller.get_all()
        assert len(contracts) == 7
        assert all(isinstance(contract, Contract) for contract in contracts)

    def test_get_depending_on_flags(self):
        """Test that contracts are well returned depending on the flags."""
        # the flags are mutually exclusive
        with pytest.raises(ValueError):
            self.controller.get_depending_on_flags(True, True, True)
        with pytest.raises(ValueError):
            self.controller.get_depending_on_flags(True, True, False)
        with pytest.raises(ValueError):
            self.controller.get_depending_on_flags(True, False, True)
        with pytest.raises(ValueError):
            self.controller.get_depending_on_flags(False, True, True)

        # None if all flags are False
        contracts = self.controller.get_depending_on_flags(False, False, False)
        assert contracts is None

        # Test each flag
        unpaid_contracts = self.controller.get_depending_on_flags(
            unpaid=True, unsigned=False, noevent=False
        )
        assert all(isinstance(contract, Contract) for contract in unpaid_contracts)
        assert all(contract.due_amount > 0 for contract in unpaid_contracts)
        assert len(unpaid_contracts) == 6

        unsigned_contracts = self.controller.get_depending_on_flags(
            unpaid=False, unsigned=True, noevent=False
        )
        assert all(isinstance(contract, Contract) for contract in unsigned_contracts)
        assert all(not contract.signed for contract in unsigned_contracts)
        assert len(unsigned_contracts) == 3

        noevent_contracts = self.controller.get_depending_on_flags(
            unpaid=False, unsigned=False, noevent=True
        )
        assert all(isinstance(contract, Contract) for contract in noevent_contracts)
        assert all(contract.event is None for contract in noevent_contracts)
        assert len(noevent_contracts) == 4

    def test_get_salesperson_supervised(self, mocker):
        """Test that the method returns the contracts of the current user's clients."""
        # login with a salesperson
        log_in("aquentin@sales.com", "Passw0rd", self.employee_repo)
        # change the get_current_user method to get_current_user_test
        mocker.patch(
            "epic_events_crm.controllers.contracts.get_current_user",
            new=self.get_current_user_test,
        )

        # Noevent flag set to False
        contracts = self.controller.get_salesperson_supervised(noevent=False)
        assert all(contract.client.salesperson_id == 4 for contract in contracts)
        assert len(contracts) == 5
        # Noevent flag set to True
        contracts = self.controller.get_salesperson_supervised(noevent=True)
        assert all(contract.client.salesperson_id == 4 for contract in contracts)
        assert len(contracts) == 4
        assert all(contract.event is None for contract in contracts)

        # login with a non-salesperson returns None
        log_in("pmercedes@supp.com", "Passw0rd", self.employee_repo)
        contracts = self.controller.get_salesperson_supervised(noevent=False)
        assert contracts is None
