from sqlalchemy import inspect, text


class TestTestingSetup:
    """Test the database setup for testing is correct."""

    def test_db_schema(self, session):
        """Check the tables in the database"""
        inspector = inspect(session.bind)
        # Check that the required tables exist
        assert "departments" in inspector.get_table_names()
        assert "permissions" in inspector.get_table_names()
        assert "department_permission" in inspector.get_table_names()
        assert "employees" in inspector.get_table_names()
        assert "clients" in inspector.get_table_names()
        assert "contracts" in inspector.get_table_names()
        assert "events" in inspector.get_table_names()

        # # Print the tables in the database if run with -s option
        # print("\nTables in the database:")
        # for table_name in inspector.get_table_names():
        #     print(table_name)

    def test_table_departments(self, session):
        """Check the content of the departments table"""
        departments = session.execute(text("SELECT * FROM departments ORDER BY id"))
        # Check that the required departments exist
        expected_departments_names = ["Superuser", "Management", "Sales", "Support"]
        for department in departments:
            assert department.name in expected_departments_names
            expected_departments_names.remove(department.name)

        # # Print the tables in the database if run with -s option
        # print("\nDepartments:")
        # for department in departments:
        #     print(department)

    def test_table_permissions(self, session):
        """Check the content of the permissions table"""
        permissions = session.execute(text("SELECT * FROM permissions ORDER BY id"))
        # Check that the required permissions exist
        expected_permissions_names = [
            "create_employee",
            "update_employee",
            "delete_employee",
            "create_client",
            "update_client",
            "delete_client",
            "create_contract",
            "update_contract",
            "delete_contract",
            "create_event",
            "update_event",
            "delete_event",
        ]
        for permission in permissions:
            assert permission.name in expected_permissions_names
            expected_permissions_names.remove(permission.name)

        # # Print the tables in the database if run with -s option
        # print("\nPermissions:")
        # for permission in permissions:
        #     print(permission)

    def test_table_department_permission(self, session):
        """Check the content of the department_permission table"""
        department_permissions = session.execute(
            text(
                """
                SELECT d.name, d.id, p.name, p.id
                FROM department_permission dp
                JOIN departments d ON dp.department_id = d.id
                JOIN permissions p ON dp.permission_id = p.id
                ORDER BY d.id
                """
            )
        )
        # Check that the table is not empty
        assert department_permissions.rowcount > 0

        # # Print the tables in the database if run with -s option
        # print("\nDepartment_permissions:")
        # for (
        #     department_name,
        #     department_id,
        #     permission_name,
        #     permission_id,
        # ) in department_permissions:
        #     print(
        #         f"{department_name} ({department_id}), "
        #         f"{permission_name} ({permission_id})"
        #     )
