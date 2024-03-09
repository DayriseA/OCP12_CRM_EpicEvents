"""
This script will initialize the MySQL database and create the necessary users for the
application. Remember that in real-world scenarios, you should never store sensitive
information like passwords in plain text or environment variables. Use a secure password
manager or encryption techniques (it may be worth to look into HashiCorp Vault, AWS
Secrets Manager or Azure Key Vault). For this school project, we will do our best
considering that the local environment is secure enough and safe from unauthorized
access.
"""

import configparser
import getpass
import os
import sys

import click
import pymysql
from cryptography.fernet import Fernet
from dotenv import set_key


def connect_to_mysql_instance(user, host, password, port=3306):
    """
    Connect to the MySQL instance.
    """
    try:
        connection = pymysql.connect(host=host, user=user, password=password, port=port)
        return connection
    except pymysql.err.OperationalError:
        click.echo("Connection failed: please check your username and password.")
        sys.exit(1)
    except pymysql.Error as err:
        click.echo(f"Error connecting to MySQL instance: {err}")
        sys.exit(1)


def create_database(connection, db_name):
    """Create a database using the provided connection and database name."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            connection.commit()
    except pymysql.Error as err:
        click.echo(f"Error creating database: {err}")
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
        click.echo(f"Error creating user: {err}")
        sys.exit(1)


def prompt_for_password(prompt_msg):
    """Prompt the user for password twice and return the value if both match."""
    while True:
        password = getpass.getpass(prompt_msg)
        password_confirm = getpass.getpass("Confirm password: ")
        if password == password_confirm:
            return password
        else:
            click.echo("Passwords do not match. Please try again.")


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


@init.command(name="db")
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
    click.echo(
        "Passwords encrypted and stored in .env file. Don't forget to save the "
        "key! (it will not be shown again)"
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
        click.echo(f"Error granting privileges: {err}")
        raise err


@init.command(name="jwt-key")
def set_jwt_secret():
    """Set the JWT_SECRET in the .env file."""
    # Prompt for the JWT secret and encrypt it
    plain_jwt_secret = input("Enter the JWT secret: ")
    encrypted_jwt_secret = fernet.encrypt(plain_jwt_secret.encode()).decode()
    # Store it in the .env file
    set_key(".env", "JWT_SECRET", encrypted_jwt_secret)


if __name__ == "__main__":
    init()
