import datetime
import os
import jwt
from dotenv import load_dotenv, set_key
from cryptography.fernet import Fernet
from typing import TYPE_CHECKING

from epic_events_crm.controllers.employees import EmployeeController
from epic_events_crm.views.base import BaseView

if TYPE_CHECKING:
    from epic_events_crm.models.employees import Employee

base_view = BaseView()
controller = EmployeeController()


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
        "hash": employee.password,
        "exp": expiration,
    }
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


def log_in(email: str, password: str, controller=controller) -> bool:
    """
    After being authenticated, log in an employee. A JWT token is created and
    stored in an environment variable.
    """
    if authenticate(email, password, controller=controller):
        employee = controller.get_by_email(email)
        token = make_jwt_token(employee)
        set_key(".env", "JWT_TOKEN", token)
        return True
    return False


def valid_token_in_env() -> bool:
    """Check if a valid JWT token is stored in the environments variables."""
    load_dotenv()
    token = os.getenv("JWT_TOKEN")
    if token is not None:
        jwt_secret = get_jwt_secret()
        try:
            jwt.decode(token, jwt_secret, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            print("The token has expired.")
        except jwt.InvalidSignatureError:
            print("The token signature is invalid.")
        except jwt.InvalidTokenError:
            print("The token is invalid.")

    return False
