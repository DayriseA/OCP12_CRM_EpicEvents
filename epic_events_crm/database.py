import getpass
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session


def make_db_url() -> URL:
    """Use the .env file to build and return a database URL object."""
    # Load the environment variables from the .env file
    load_dotenv()
    db_user = os.getenv("APP_USER")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    # Get and decrypt the password
    if os.getenv("EECRM_KEY"):
        key = os.getenv("EECRM_KEY")
    else:
        key = getpass.getpass("Enter the key to decrypt the password: ")
    encrypted_password = os.getenv("APP_PWD")
    fernet = Fernet(key)
    password = fernet.decrypt(encrypted_password.encode()).decode()
    # We use URL.create to handle special characters like @ in the password
    url = URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=password,
        host=db_host,
        port=db_port,
        database=db_name,
    )
    return url


def get_session() -> Session:
    """Return a SQLAlchemy session."""
    engine = create_engine(make_db_url())
    session = Session(engine)
    return session


def make_test_db_url() -> URL:
    """Use the .env file to build and return the test database URL object."""
    # Load the environment variables from the .env file
    load_dotenv()
    db_user = os.getenv("APP_USER")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_TEST_NAME")
    # Get and decrypt the password
    if os.getenv("EECRM_KEY"):
        key = os.getenv("EECRM_KEY")
    else:
        key = getpass.getpass("Enter the key to decrypt the password: ")
    encrypted_password = os.getenv("APP_PWD")
    fernet = Fernet(key)
    password = fernet.decrypt(encrypted_password.encode()).decode()
    # We use URL.create to handle special characters like @ in the password
    url = URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=password,
        host=db_host,
        port=db_port,
        database=db_name,
    )
    return url


def get_test_session() -> Session:
    """Return a SQLAlchemy session for testing purposes."""
    engine = create_engine(make_test_db_url())
    session = Session(engine)
    return session


def get_state_name(obj) -> str:
    """An utility function to the state of an object."""
    inspector = inspect(obj)
    state_name = "UNKNOWN"
    if inspector.transient:
        state_name = "TRANSIENT"
    elif inspector.pending:
        state_name = "PENDING"
    elif inspector.persistent:
        state_name = "PERSISTENT"
    elif inspector.deleted:
        state_name = "DELETED"
    elif inspector.detached:
        state_name = "DETACHED"
    return state_name
