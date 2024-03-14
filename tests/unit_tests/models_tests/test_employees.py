import importlib
from argon2 import PasswordHasher

from epic_events_crm.models.employees import Employee

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


class TestEmployeeModel:
    """Unit tests related to the Employee model and its methods."""

    def setup_method(self):
        """Setup for each test method."""
        self.employee = Employee(password=" ")

    def test_set_password(self):
        """Test that the password is hashed and set correctly."""
        ph = PasswordHasher()
        self.employee.set_password("azerty-123")
        assert ph.verify(self.employee.password, "azerty-123")

    def test_set_password_changes_password(self):
        """Test that the password is changed"""
        self.employee.set_password("azerty-123")
        old_hash = self.employee.password
        self.employee.set_password("different-password")
        assert old_hash != self.employee.password

    def test_check_password(self):
        """Test that check_password correctly verifies the password."""
        self.employee.set_password("azerty-123")
        assert self.employee.check_password("azerty-123")

    def test_check_password_wrong_password(self):
        """Test that False is returned when the password is wrong."""
        self.employee.set_password("azerty-123")
        assert self.employee.check_password("wrong-password") is False
