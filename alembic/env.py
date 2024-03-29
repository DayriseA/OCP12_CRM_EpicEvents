import getpass
import importlib
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

from logging.config import fileConfig

from sqlalchemy import pool, create_engine
from sqlalchemy.engine import URL

from alembic import context

from epic_events_crm.models import Base

WANTED_MODULES = (
    "epic_events_crm.models.employees",
    "epic_events_crm.models.departments_permissions",
    "epic_events_crm.models.clients",
    "epic_events_crm.models.contracts",
    "epic_events_crm.models.events",
)

for module in WANTED_MODULES:
    try:
        loaded_module = importlib.import_module(module)
    except Exception as e:
        print(f"Could not import module {module}.")
        print(f"Error: {e}")

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # ORIGINAL COMMENTED OUT
    # url = config.get_main_option("sqlalchemy.url")
    # context.configure(
    #     url=url,
    #     target_metadata=target_metadata,
    #     literal_binds=True,
    #     dialect_opts={"paramstyle": "named"},
    # )

    db_driver = "mysql"
    db_name = os.getenv("DB_NAME")
    url = f"{db_driver}:///{db_name}"
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # ORIGINAL COMMENTED OUT
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )

    # Load infos from the .env file
    db_user = os.getenv("MIGRATIONS_USER")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    # db_name is first checked in the config (sometime programmatically set to test db)
    db_config_name = config.get_main_option("sqlalchemy.database")
    if db_config_name:
        db_name = db_config_name
    else:
        db_name = os.getenv("DB_NAME")

    # Get and decrypt the password
    if os.getenv("EECRM_KEY"):
        key = os.getenv("EECRM_KEY")
    else:
        key = getpass.getpass("Enter the key to decrypt the password: ")
    encrypted_password = os.getenv("MIGRATIONS_PWD")
    fernet = Fernet(key)
    password = fernet.decrypt(encrypted_password.encode()).decode()

    # Create connection, URL.create to handle special characters like @ in password
    url = URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=password,
        host=db_host,
        port=db_port,
        database=db_name,
    )
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
