from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
import datetime

from sqlalchemy import String, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql import func

from . import Base

if TYPE_CHECKING:
    from .employees import Employee
    from .contracts import Contract


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    fname: Mapped[str] = mapped_column(String(50), nullable=False)
    lname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255))
    salesperson_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    salesperson: Mapped[Employee] = relationship(back_populates="clients")
    contracts: Mapped[List[Contract]] = relationship(back_populates="client")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # https://docs.sqlalchemy.org/en/20/dialects/mysql.html#mysql-timestamp-onupdate
    last_updated: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )
