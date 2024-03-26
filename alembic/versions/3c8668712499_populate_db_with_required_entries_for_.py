"""populate db with required entries for app

Revision ID: 3c8668712499
Revises: de275cc8b0f2
Create Date: 2024-03-25 08:22:01.163451

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = "3c8668712499"
down_revision: Union[str, None] = "de275cc8b0f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Define the tables
    departments = table("departments", column("name", sa.String))
    permissions = table("permissions", column("name", sa.String))
    department_permission = table(
        "department_permission",
        column("department_id", sa.Integer),
        column("permission_id", sa.Integer),
    )

    # Insert departments
    op.bulk_insert(
        departments,
        [
            {"name": "Superuser"},
            {"name": "Management"},
            {"name": "Sales"},
            {"name": "Support"},
        ],
    )

    # Insert permissions
    op.bulk_insert(
        permissions,
        [
            {"name": "create_employee"},
            {"name": "update_employee"},
            {"name": "delete_employee"},
            {"name": "create_client"},
            {"name": "update_client"},
            {"name": "delete_client"},
            {"name": "create_contract"},
            {"name": "update_contract"},
            {"name": "delete_contract"},
            {"name": "create_event"},
            {"name": "update_event"},
            {"name": "delete_event"},
        ],
    )

    # Link permissions to departments
    op.bulk_insert(
        department_permission,
        [
            {"department_id": 2, "permission_id": 1},
            {"department_id": 2, "permission_id": 2},
            {"department_id": 2, "permission_id": 3},
            {"department_id": 2, "permission_id": 7},
            {"department_id": 2, "permission_id": 8},
            {"department_id": 2, "permission_id": 11},
            {"department_id": 3, "permission_id": 4},
            {"department_id": 3, "permission_id": 5},
            {"department_id": 3, "permission_id": 6},
            {"department_id": 3, "permission_id": 8},
            {"department_id": 3, "permission_id": 10},
            {"department_id": 4, "permission_id": 11},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM department_permission")
    op.execute("DELETE FROM permissions")
    op.execute("DELETE FROM departments")
