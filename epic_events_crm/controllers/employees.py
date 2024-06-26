from typing import Optional, List
from pymysql.err import IntegrityError
from sentry_sdk import capture_message
from sqlalchemy import exc

from epic_events_crm.authentication import get_current_user
from epic_events_crm.utilities import is_email_valid
from epic_events_crm.database import get_session
from epic_events_crm.models.employees import Employee
from epic_events_crm.repositories.employees import EmployeeRepo
from epic_events_crm.controllers.departments_permissions import DepartmentController


class EmployeeController:
    """
    Employee controller class. If no session is provided to constructor,
    a new one is created.
    """

    def __init__(self, session=None):
        if session is not None:
            self.session = session
        else:
            self.session = get_session()
        self.repo = EmployeeRepo(self.session)
        self.department_controller = DepartmentController(self.session)

    def create(
        self, fname: str, lname: str, email: str, password: str, department_id: int
    ) -> None:
        """
        Create an employee and add it to the database.
        Can't create in the Superuser department.
        """
        # Check if email is valid
        if not is_email_valid(email):
            raise ValueError("Invalid email.")
        # Check if email is not already used
        if self.repo.get_by_email(email):
            raise ValueError("Email already in use.")
        # Format first and last name
        fname = fname.title()
        lname = lname.upper()
        # Check if department exists. If not raise error with a list of departments
        if not self.department_controller.repo.get_by_id(department_id):
            msg = self.department_controller.display_all()
            raise ValueError(f"Department id not found. {msg}")
        # Prevent from creating an employee in the Superuser department
        superuser_dpt = self.department_controller.repo.get_by_name("Superuser")
        if department_id == superuser_dpt.id:
            raise PermissionError("You are not allowed to create a superuser.")

        employee = Employee(
            fname=fname,
            lname=lname,
            email=email,
            password=password,
            department_id=department_id,
        )
        self.repo.add(employee)
        try:
            current_user = get_current_user() or "Unknown user (most likely non CLI)"
            self.session.commit()
            capture_message(f"{current_user} created new {employee}", level="info")
        except exc.SQLAlchemyError as e:
            raise exc.SQLAlchemyError(f"Error: {e}")

    def update(
        self,
        employee_id: Optional[int] = None,
        email: Optional[str] = None,
        fname: Optional[str] = None,
        lname: Optional[str] = None,
        department_id: Optional[int] = None,
    ) -> None:
        """
        Update an employee's details. Employee is identified by id or email.
        Password cannot be changed with this method. Must provide id if email is to
        be updated.
        """
        if not employee_id and not email:
            raise ValueError("Provide either employee id or email.")
        # Get employee by id or email
        if employee_id is not None:
            employee = self.repo.get_by_id(employee_id)
            if employee is None:
                raise ValueError("Employee not found.")
            # If employee id and email are provided, update email (if valid)
            if email is not None:
                if is_email_valid(email) and not self.repo.get_by_email(email):
                    employee.email = email
                else:
                    raise ValueError("Email invalid or already used.")
        else:
            employee = self.repo.get_by_email(email)
        if employee is None:
            raise ValueError("Employee not found.")

        # Update employee's details
        if fname is not None:
            employee.fname = fname.title()
        if lname is not None:
            employee.lname = lname.upper()
        if department_id is not None:
            if self.department_controller.repo.get_by_id(department_id):
                employee.department_id = department_id
            else:
                msg = self.department_controller.display_all()
                raise ValueError(f"Department id not found. {msg}")

        try:
            current_user = get_current_user() or "Unknown user (most likely non CLI)"
            self.session.commit()
            capture_message(f"{current_user} updated {employee}", level="info")
        except exc.SQLAlchemyError as e:
            raise exc.SQLAlchemyError(f"Error: {e}")

    def delete(self, employee: Employee) -> None:
        """Delete an employee from the database."""
        self.repo.delete(employee)
        try:
            self.session.commit()
        except exc.SQLAlchemyError as e:
            # Specific error for employee still assigned to a client
            msg = "'salesperson_id' cannot be null"
            if isinstance(e.orig, IntegrityError) and msg in e.orig.args[1]:

                raise exc.SQLAlchemyError("Employee still assigned to a client.")
            raise exc.SQLAlchemyError(f"Error trying to commit deletion: {e}")

    def get_all(self) -> Optional[List[Employee]]:
        """Return all employees."""
        return self.repo.get_all()

    def create_superuser(
        self, fname: str, lname: str, email: str, password: str
    ) -> None:
        """
        Create a superuser and add it to the database.
        """
        # Check if email is valid
        if not is_email_valid(email):
            raise ValueError("Invalid email.")
        # Check if email is not already used
        if self.repo.get_by_email(email):
            raise ValueError("Email already in use.")
        # Format first and last name
        fname = fname.title()
        lname = lname.upper()
        # Get the Superuser department id
        superuser_dpt = self.department_controller.repo.get_by_name("Superuser")
        if not superuser_dpt:
            raise ValueError("No Superuser department. Follow setup instructions.")

        employee = Employee(
            fname=fname,
            lname=lname,
            email=email,
            password=password,
            department_id=superuser_dpt.id,
        )
        self.repo.add(employee)
        try:
            self.session.commit()
        except exc.SQLAlchemyError as e:
            raise exc.SQLAlchemyError(f"Error: {e}")
