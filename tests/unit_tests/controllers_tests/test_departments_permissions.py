import pytest

from epic_events_crm.controllers.departments_permissions import DepartmentController


class TestDepartmentController:
    """Test DepartmentController class."""

    @pytest.fixture(autouse=True)
    def setup_class(self, session):
        self.controller = DepartmentController(session)

    def test_display_all(self):
        """Test that display_all() returns a formatted string of all departments."""

        expected_output = "Availables departments:\nSUPERUSER (id:1)\n"
        expected_output += "MANAGEMENT (id:2)\nSALES (id:3)\nSUPPORT (id:4)\n"
        assert self.controller.display_all() == expected_output
