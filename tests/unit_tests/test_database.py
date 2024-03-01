import os
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.engine.url import URL

from epic_events_crm.database import make_test_db_url, make_db_url, get_test_session


class TestDatabase:
    """Tests related to the database module."""

    def test_uri_making(self, mocker):
        """Test to verify that the database URIs are made correctly."""
        # Mock the environment variables
        mocker.patch.dict(
            os.environ,
            {
                "APP_USER": "test_user",
                "DB_HOST": "localhost",
                "DB_PORT": "3306",
                "DB_NAME": "my_db",
                "DB_TEST_NAME": "test_db",
                "APP_PWD": "test_pwd",
                "EECRM_KEY": "g6lK6tZU0u3lIPyJ34Qlzwe9bRVSWHZP8C_F5jFtH6U=",
            },
        )
        # Mock the Fernet decrypt method
        mocker.patch("cryptography.fernet.Fernet.decrypt", return_value=b"test_pwd")

        # Call the function and assert the result
        # make_url hide the password with ***
        expected = "mysql+pymysql://test_user:***@localhost:3306/test_db"
        result = make_test_db_url()
        assert isinstance(result, URL)
        assert str(result) == expected
        expected = "mysql+pymysql://test_user:***@localhost:3306/my_db"
        result = make_db_url()
        assert isinstance(result, URL)
        assert str(result) == expected

    def test_get_test_session(self):
        """
        Test to verify that an SQLAlchemy session is returned.
        Needs the test database to be up and running.
        """
        session = get_test_session()
        assert isinstance(session, Session)
        assert isinstance(session.bind, Engine)
