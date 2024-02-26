from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import datetime

from sqlalchemy import ForeignKey, DateTime, String, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base

if TYPE_CHECKING:
    from .contracts import Contract
    from .employees import Employee


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_datetime: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_datetime: Mapped[datetime.datetime] = mapped_column(DateTime)
    address_line1: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(50))
    country: Mapped[str] = mapped_column(String(25))
    postal_code: Mapped[str] = mapped_column(String(20))
    attendees_number: Mapped[int]
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-one
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), nullable=False)
    contract: Mapped[Contract] = relationship(
        back_populates="event", single_parent=True
    )

    support_person_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"))
    support_person: Mapped[Optional[Employee]] = relationship(back_populates="events")

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    __table_args__ = (UniqueConstraint("contract_id"),)
