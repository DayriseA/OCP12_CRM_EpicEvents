import os
import pytest
from dotenv import load_dotenv
from alembic import command
from alembic.config import Config

from epic_events_crm.database import get_test_session
from epic_events_crm.views.base import BaseView

view = BaseView()


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    """Run the alembic migrations on the test database."""
    load_dotenv()
    config = Config("alembic.ini")  # Tests run from the root directory
    db_test_name = os.getenv("DB_TEST_NAME")
    config.set_main_option("sqlalchemy.database", db_test_name)
    view.display_as(f"\nUPGRADING MIGRATIONS RUNNING ON: {db_test_name}", "info")
    command.upgrade(config, "head")

    yield

    view.display_as(f"\nDOWNGRADING MIGRATIONS RUNNING ON: {db_test_name}", "info")
    command.downgrade(config, "base")


@pytest.fixture(scope="class")
def session():
    """Provide a test session as a fixture at a class scope."""
    session = get_test_session()

    yield session

    session.rollback()
    session.close()
