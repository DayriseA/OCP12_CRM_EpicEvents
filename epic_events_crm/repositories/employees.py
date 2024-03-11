from typing import List, Optional
from sqlalchemy import select

from epic_events_crm.database import get_session
from epic_events_crm.models.employees import Employee


class EmployeeRepo:
    """
    Employee repository class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()

    def add(self, employee: Employee) -> None:
        """Add an employee to the session."""
        try:
            self.session.add(employee)
        except Exception as e:
            print(f"Error adding employee: {e}")

    def get_all(self) -> List[Employee]:
        """Return all employees as a list."""
        try:
            return self.session.execute(select(Employee)).scalars().all()
        except Exception as e:
            print(f"Error getting all employees: {e}")

    def get_by_id(self, employee_id: int) -> Optional[Employee]:
        """Return an employee by its id."""
        try:
            return self.session.get(Employee, employee_id)
        except Exception as e:
            print(f"Error getting employee by id: {e}")

    def get_by_email(self, email: str) -> Optional[Employee]:
        """Return an employee by its email."""
        try:
            return self.session.execute(
                select(Employee).filter_by(email=email)
            ).scalar_one()
        except Exception as e:
            print(f"Error getting employee by email: {e}")

    def delete(self, employee: Employee) -> None:
        """Mark an employee for deletion in the session."""
        try:
            self.session.delete(employee)
        except Exception as e:
            print(f"Error deleting employee: {e}")
