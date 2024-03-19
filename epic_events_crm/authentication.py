import datetime
import os
import jwt
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
from typing import Union, Optional

from epic_events_crm.models.employees import Employee
from epic_events_crm.repositories.employees import EmployeeRepo
from epic_events_crm.views.base import BaseView


base_view = BaseView()
controller = EmployeeRepo()


def authenticate(email: str, password: str, controller=controller) -> bool:
    """Authenticate an employee by email and password."""
    employee = controller.get_by_email(email)
    if employee is not None:
        return employee.check_password(password)
    return False


def get_jwt_secret() -> str:
    """Return the JWT secret key from the crypted environment variable."""
    load_dotenv()
    if os.getenv("EECRM_KEY"):
        key = os.getenv("EECRM_KEY")
    else:
        key = base_view.ask_app_key()
    encrypted_jwt_secret = os.getenv("JWT_SECRET")
    fernet = Fernet(key)
    jwt_secret = fernet.decrypt(encrypted_jwt_secret.encode()).decode()
    return jwt_secret


def make_jwt_token(employee: "Employee") -> str:
    """Create a JWT token for an employee."""
    expiration = datetime.datetime.now() + datetime.timedelta(minutes=15)
    jwt_secret = get_jwt_secret()
    # required claims are employee id, hashed password and expiration
    payload = {
        "uid": employee.id,
        "department_id": employee.department_id,
        "exp": expiration,
    }
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


def log_in(email: str, password: str, controller=controller) -> bool:
    """
    After being authenticated, log in an employee. A JWT token is created and
    stored in a .env file.
    """
    if authenticate(email, password, controller=controller):
        employee = controller.get_by_email(email)
        token = make_jwt_token(employee)
        set_key(".env", "JWT_TOKEN", token)
        return True
    return False


def valid_token_in_env() -> Union[bool, dict]:
    """
    Check if a valid JWT token is stored in the environments variables.
    Return False if the token is invalid, expired or not present.
    If token is valid, return the payload in a dictionary.
    """
    load_dotenv()
    token = os.getenv("JWT_TOKEN")
    if token is not None:
        jwt_secret = get_jwt_secret()
        try:
            decoded_token = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            return decoded_token
        except jwt.ExpiredSignatureError:
            base_view.display_as("The token has expired.", "warning")
            return False
        except jwt.InvalidSignatureError:
            print("The token signature is invalid.", "error")
            return False
        except jwt.InvalidTokenError:
            print("The token is invalid.", "error")
            return False
    return False


def get_current_user() -> Optional[Employee]:
    """Return the current user from the JWT token."""
    token = valid_token_in_env()
    if token:
        return controller.get_by_id(token["uid"])
    return None


def requires_auth(f):
    """Decorator for requiring authentication."""

    def wrapper(*args, **kwargs):
        try:
            valid_token = valid_token_in_env()
        except Exception as e:
            base_view.display_as(f"Error: {e}", "error")
        if valid_token:
            return f(*args, **kwargs)

    return wrapper
