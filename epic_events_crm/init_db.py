"""
This script will initialize the MySQL database and create the necessary users for the
application. Remember that in real-world scenarios, you should never store sensitive
information like passwords in plain text or environment variables. Use a secure password
manager or encryption techniques (it may be worth to look into HashiCorp Vault, AWS
Secrets Manager or Azure Key Vault). A standard employee in scenario should never have
access to the commands defined in this module.
For this school project we will do our best, assuming that the local environment is
secure enough and safe from unauthorized access.
"""

import configparser
import getpass
import importlib
import os
import sys

import click
import pymysql
from cryptography.fernet import Fernet
from dotenv import set_key, load_dotenv
from epic_events_crm.views.base import BaseView

view = BaseView()


def connect_to_mysql_instance(user, host, password, port=3306):
    """
    Connect to the MySQL instance.
    """
    try:
        connection = pymysql.connect(host=host, user=user, password=password, port=port)
        return connection
    except pymysql.err.OperationalError:
        view.display_as(
            "Connection failed: please check your username and password.", "error"
        )
        sys.exit(1)
    except pymysql.Error as err:
        view.display_as(f"Error connecting to MySQL instance: {err}", "error")
        sys.exit(1)


def create_database(connection, db_name):
    """Create a database using the provided connection and database name."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            connection.commit()
    except pymysql.Error as err:
        view.display_as(f"Error creating database: {err}", "error")
        sys.exit(1)


def create_user(connection, username, password, host):
    """Create a user using the provided connection, db_name, username and password."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE USER IF NOT EXISTS '{username}'@'{host}' IDENTIFIED BY '{password}'"  # noqa
            )
            connection.commit()
    except pymysql.Error as err:
        view.display_as(f"Error creating user: {err}", "error")
        sys.exit(1)


def prompt_for_password(prompt_msg):
    """Prompt the user for password twice and return the value if both match."""
    while True:
        password = getpass.getpass(prompt_msg)
        password_confirm = getpass.getpass("Please confirm: ")
        if password == password_confirm:
            return password
        else:
            view.display_as("Confirmation not matching. Please try again.", "warning")


# get infos from the config file, regardless of the current working directory
dir_path = os.path.dirname(os.path.realpath(__file__))
config_file_path = os.path.join(dir_path, "config.ini")
config = configparser.ConfigParser()
config.read(config_file_path)

# Generate a key for the encryption and decryption
key = Fernet.generate_key()
fernet = Fernet(key)


@click.group()
def init():
    pass


@init.command(name="db", short_help="Initialize the MySQL database and users.")
@click.option(
    "-u",
    "--user",
    prompt=True,
    help="The user with rights to create databases, users and grant privileges.",
)
@click.option(
    "-h",
    "--host",
    default=config.get("db-init", "host", fallback="localhost"),
    help="The host where the MySQL instance is running. Defaults to localhost.",
)
@click.option(
    "-p",
    "--port",
    default=int(config.get("db-init", "port", fallback=3306)),
    help="MySQL port. Defaults to 3306.",
)
def initialize_database(user, host, port):
    """
    Main function to initialize the MySQL database and create the necessary users.
    Also grant them the necessary privileges. Passwords are encrypted using Fernet and
    stored in a .env file. The user must save the key before quitting the terminal.
    """
    db_name = config.get("db-init", "db_name", fallback="ee_crm_db")
    migrations_username = config.get(
        "db-init", "migrations_username", fallback="ee_crm_migrations"
    )
    app_username = config.get("db-init", "app_username", fallback="ee_crm_app")

    # prompt for the user password and try to connect to the MySQL instance
    password = getpass.getpass("Enter your MySQL password:")
    connection = connect_to_mysql_instance(user, host, password, port)

    # prompt for the passwords for the migrations and app users
    migrations_pwd = prompt_for_password("Enter the password for the migrations user:")
    app_pwd = prompt_for_password("Enter the password for the app user:")

    create_database(connection, db_name)
    create_user(connection, migrations_username, migrations_pwd, host)
    create_user(connection, app_username, app_pwd, host)

    # Once the users are created, encrypt the passwords and store them in a .env file
    # Encryption operates on bytes and storing in a .env file requires strings
    migrations_pwd_encrypted = fernet.encrypt(migrations_pwd.encode()).decode()
    app_pwd_encrypted = fernet.encrypt(app_pwd.encode()).decode()
    set_key(".env", "MIGRATIONS_PWD", migrations_pwd_encrypted)
    set_key(".env", "APP_PWD", app_pwd_encrypted)
    view.display_as(
        "Passwords encrypted and stored in .env file. Don't forget to save the "
        "key! (it will not be shown again)",
        "warning",
    )
    click.echo(f"Key: {key.decode()}")

    # if host or port provided as options differ from the config file, update it
    # remind that config.get always returns a string
    if str(host) != config.get("db-init", "host"):
        config.set("db-init", "host", host)
    if str(port) != config.get("db-init", "port"):
        config.set("db-init", "port", str(port))
    # also update the .env file with the config values for further use
    set_key(".env", "DB_HOST", host)
    set_key(".env", "DB_PORT", str(port))
    set_key(".env", "DB_NAME", db_name)
    set_key(".env", "MIGRATIONS_USER", migrations_username)
    set_key(".env", "APP_USER", app_username)

    # define privileges for the created users, trying to respect the principle
    # of least privilege
    migrations_stmt = (
        f"GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, REFERENCES "
        f"ON {db_name}.* TO '{migrations_username}'@'{host}'"
    )
    app_stmt = (
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON {db_name}.* TO "
        f"'{app_username}'@'{host}'"
    )
    # grant the privileges
    try:
        with connection.cursor() as cursor:
            cursor.execute(migrations_stmt)
            cursor.execute(app_stmt)
            connection.commit()
    except pymysql.Error as err:
        view.display_as(f"Error granting privileges: {err}", "error")
        raise err


@init.command(name="test-db", short_help="Initialize the MySQL test database.")
@click.option(
    "-u",
    "--user",
    prompt=True,
    help="The user with rights to create databases, users and grant privileges.",
)
def initialize_test_database(user):
    """
    Initialize the MySQL test database.
    Must be run after the main database is initialized.
    """
    # Load the environment variables from the .env file
    load_dotenv()
    app_user = os.getenv("APP_USER")
    migrations_user = os.getenv("MIGRATIONS_USER")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    # Set test database name based on the main database name
    db_test_name = db_name + "_test"
    set_key(".env", "DB_TEST_NAME", db_test_name)

    # Connect to the MySQL instance
    password = getpass.getpass("Enter your MySQL password:")
    connection = connect_to_mysql_instance(user, db_host, password, int(db_port))

    # Create the test database
    create_database(connection, db_test_name)

    # Grant all privileges on the test database
    app_stmt = f"GRANT ALL PRIVILEGES ON {db_test_name}.* TO '{app_user}'@'{db_host}'"
    migrations_stmt = (
        f"GRANT ALL PRIVILEGES ON {db_test_name}.* TO '{migrations_user}'@'{db_host}'"
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(app_stmt)
            cursor.execute(migrations_stmt)
            connection.commit()
    except pymysql.Error as err:
        view.display_as(f"Error granting privileges: {err}", "error")
        raise err


@init.command(name="jwt-key", short_help="Set the JWT secret key.")
def set_jwt_secret():
    """Set the JWT_SECRET in the .env file."""
    # Prompt for the JWT secret and encrypt it
    plain_jwt_secret = prompt_for_password("Define the JWT secret: ")
    encrypted_jwt_secret = fernet.encrypt(plain_jwt_secret.encode()).decode()
    # Store it in the .env file
    set_key(".env", "JWT_SECRET", encrypted_jwt_secret)
    view.display_as("JWT secret successfully set and stored.", "info")


@init.command(name="create-superuser", short_help="Infos will be prompted.")
def create_superuser():
    """Create a superuser for the application in the database."""
    from epic_events_crm.controllers.employees import EmployeeController

    NEEDED_MODULES = (
        "epic_events_crm.models.clients",
        "epic_events_crm.models.contracts",
        "epic_events_crm.models.events",
    )
    for module in NEEDED_MODULES:
        try:
            importlib.import_module(module)
        except ImportError:
            view.display_as(f"Could not import module {module}.", "error")

    controller = EmployeeController()
    fname = click.prompt("First name")
    lname = click.prompt("Last name")
    email = click.prompt("Email")
    password = prompt_for_password("Password: ")

    try:
        controller.create_superuser(fname, lname, email, password)
        view.display_as("Superuser created successfully.", "info")
    except Exception as e:
        view.display_as(f"Error creating superuser: {e}", "error")


if __name__ == "__main__":
    init()
