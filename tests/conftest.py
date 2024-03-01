import pytest

from epic_events_crm.database import get_test_session


@pytest.fixture(scope="class")
def session():
    """Provide a test session as a fixture at a class scope."""
    session = get_test_session()
    yield session
    session.rollback()
    session.close()
