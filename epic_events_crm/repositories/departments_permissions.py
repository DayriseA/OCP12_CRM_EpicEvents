from typing import List, Optional
from sqlalchemy import select

from epic_events_crm.database import get_session
from epic_events_crm.models.departments_permissions import Department, Permission


class DepartmentRepo:
    """
    Department repository class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()

    def add(self, department: Department) -> None:
        """Add a department to the session."""
        try:
            self.session.add(department)
        except Exception as e:
            print(f"Error adding department: {e}")

    def get_all(self) -> List[Department]:
        """Return all departments as a list."""
        try:
            return (
                self.session.execute(select(Department).order_by(Department.id))
                .scalars()
                .all()
            )
        except Exception as e:
            print(f"Error getting all departments: {e}")

    def get_by_id(self, department_id: int) -> Optional[Department]:
        """Return a department by its id."""
        try:
            return self.session.get(Department, department_id)
        except Exception as e:
            print(f"Error getting department by id: {e}")

    def get_by_name(self, name: str) -> Optional[Department]:
        """Return a department by its name."""
        try:
            return self.session.execute(
                select(Department).filter_by(name=name)
            ).scalar_one_or_none()
        except Exception as e:
            print(f"Error getting department by name: {e}")

    def delete(self, department: Department) -> None:
        """Mark a department for deletion in the session."""
        try:
            self.session.delete(department)
        except Exception as e:
            print(f"Error deleting department: {e}")


class PermissionRepo:
    """
    Permission repository class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()

    def add(self, permission: Permission) -> None:
        """Add a permission to the session."""
        try:
            self.session.add(permission)
        except Exception as e:
            print(f"Error adding permission: {e}")

    def get_all(self) -> List[Permission]:
        """Return all permissions as a list."""
        try:
            return self.session.execute(select(Permission)).scalars().all()
        except Exception as e:
            print(f"Error getting all permissions: {e}")

    def get_by_id(self, permission_id: int) -> Optional[Permission]:
        """Return a permission by its id."""
        try:
            return self.session.get(Permission, permission_id)
        except Exception as e:
            print(f"Error getting permission by id: {e}")

    def get_by_name(self, name: str) -> Optional[Permission]:
        """Return a permission by its name."""
        try:
            return self.session.execute(
                select(Permission).filter_by(name=name)
            ).scalar_one_or_none()
        except Exception as e:
            print(f"Error getting permission by name: {e}")

    def delete(self, permission: Permission) -> None:
        """Mark a permission for deletion in the session."""
        try:
            self.session.delete(permission)
        except Exception as e:
            print(f"Error deleting permission: {e}")
