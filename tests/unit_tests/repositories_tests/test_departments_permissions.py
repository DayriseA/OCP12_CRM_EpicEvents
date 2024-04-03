import pytest
from sqlalchemy import inspect, exc

from epic_events_crm.models.departments_permissions import Department, Permission
from epic_events_crm.repositories.departments_permissions import DepartmentRepo
from epic_events_crm.repositories.departments_permissions import PermissionRepo


class TestDepartmentRepo:
    """Test DepartmentRepo class."""

    @pytest.fixture(autouse=True)
    def setup_class(self, session):
        self.repo = DepartmentRepo(session)

    def test_add(self):
        """Test that the department is added to the session."""
        department = Department(name="Sales_test")
        department_2 = Department(name="Support_test")
        self.repo.add(department)
        assert inspect(department).pending
        self.repo.session.flush()
        assert inspect(department).persistent
        self.repo.add(department_2)
        assert inspect(department_2).pending

    def test_get_by_name(self):
        """Test that a department is obtained by its name."""
        department = self.repo.get_by_name("Support_test")
        assert isinstance(department, Department)
        assert department.name == "Support_test"

        # as a side effect the query changed the state from pending to persistent
        assert inspect(department).persistent

    def test_get_by_id(self):
        """Test that a department is obtained by its id."""
        department = self.repo.get_by_id(1)
        assert isinstance(department, Department)

    def test_get_all(self):
        """Test the method returns all departments as a Department list."""
        departments = self.repo.get_all()
        assert isinstance(departments, list)
        assert all(isinstance(department, Department) for department in departments)

    def test_delete(self):
        """Test that a department is marked for deletion in the session."""
        department = self.repo.get_by_name("Support_test")
        self.repo.delete(department)
        # from epic_events_crm.database import get_state_name
        # state_name = get_state_name(department)
        # print(f"Department state: {state_name}")
        # we have to flush else its still shows as persistent
        self.repo.session.flush()
        assert inspect(department).deleted

    def test_add_existing_name(self):
        """Test add method with an existing name."""
        department = Department(name="Sales_test")
        self.repo.add(department)  # No error because it's still pending
        with pytest.raises(exc.IntegrityError):
            self.repo.session.flush()


class TestPermissionRepo:
    """Test PermissionRepo class."""

    @pytest.fixture(autouse=True)
    def setup_class(self, session):
        self.repo = PermissionRepo(session)

    def test_add(self):
        """Test that the permission is added to the session."""
        permission = Permission(name="Create_test")
        permission_2 = Permission(name="Delete_test")
        self.repo.add(permission)
        assert inspect(permission).pending
        self.repo.session.flush()
        assert inspect(permission).persistent
        self.repo.add(permission_2)
        assert inspect(permission_2).pending

    def test_get_by_name(self):
        """Test that a permission is obtained by its name."""
        permission = self.repo.get_by_name("Delete_test")
        assert isinstance(permission, Permission)
        assert permission.name == "Delete_test"

        # as a side effect the query changed the state from pending to persistent
        assert inspect(permission).persistent

    def test_get_by_id(self):
        """Test that a permission is obtained by its id."""
        permission = self.repo.get_by_id(1)
        assert isinstance(permission, Permission)

    def test_get_all(self):
        """Test the method returns all permissions as a Permission list."""
        permissions = self.repo.get_all()
        assert isinstance(permissions, list)
        assert all(isinstance(permission, Permission) for permission in permissions)

    def test_delete(self):
        """Test that a permission is marked for deletion in the session."""
        permission = self.repo.get_by_name("Delete_test")
        self.repo.delete(permission)
        # we have to flush else its still shows as persistent
        self.repo.session.flush()
        assert inspect(permission).deleted

    def test_add_existing_name(self):
        """Test add method with an existing name."""
        permission = Permission(name="Create_test")
        self.repo.add(permission)  # No error because it's still pending
        with pytest.raises(exc.IntegrityError):
            self.repo.session.flush()
        self.repo.session.rollback()
