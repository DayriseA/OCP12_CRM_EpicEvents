from __future__ import annotations
from typing import List, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    from .employees import Employee

department_permission = Table(
    "department_permission",
    Base.metadata,
    Column("department_id", ForeignKey("departments.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    employees: Mapped[List[Employee]] = relationship(back_populates="department")
    permissions: Mapped[List[Permission]] = relationship(
        secondary=department_permission, back_populates="departments"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    departments: Mapped[List[Department]] = relationship(
        secondary=department_permission, back_populates="permissions"
    )
