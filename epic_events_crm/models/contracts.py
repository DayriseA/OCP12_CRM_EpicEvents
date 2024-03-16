from __future__ import annotations
from typing import TYPE_CHECKING
from decimal import Decimal
import datetime

from sqlalchemy import ForeignKey, DECIMAL, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from . import Base

if TYPE_CHECKING:
    from .clients import Client
    from .events import Event


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    client: Mapped[Client] = relationship(back_populates="contracts")
    event: Mapped[Event] = relationship(back_populates="contract")
    total_amount: Mapped[Decimal] = mapped_column(DECIMAL(15, 2), nullable=False)
    due_amount: Mapped[Decimal] = mapped_column(DECIMAL(15, 2), nullable=False)
    signed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    def __repr__(self) -> str:
        fname = self.client.fname
        lname = self.client.lname
        if self.event:
            return (
                f"<Contract id:{self.id} for {fname} {lname} on event "
                f"{self.event.name}. Signed: {self.signed}>"
            )
        else:
            return f"<Contract id:{self.id} for {fname} {lname}. Signed: {self.signed}>"
