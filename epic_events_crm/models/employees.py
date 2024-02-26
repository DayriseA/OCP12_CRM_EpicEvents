from __future__ import annotations
from typing import TYPE_CHECKING, List
import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base

if TYPE_CHECKING:
    from .departments_permissions import Department
    from .clients import Client
    from .events import Event


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    fname: Mapped[str] = mapped_column(String(50))
    lname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id"), nullable=False
    )
    department: Mapped[Department] = relationship(back_populates="employees")
    clients: Mapped[List[Client]] = relationship(back_populates="salesperson")
    events: Mapped[List[Event]] = relationship(back_populates="support_person")

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
