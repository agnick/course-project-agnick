from __future__ import annotations

from sqlalchemy import CheckConstraint, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db_base import Base


class WishORM(Base):
    __tablename__ = "wishes"

    owner: Mapped[str] = mapped_column(String(64), primary_key=True)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(50), nullable=False)
    link: Mapped[str | None] = mapped_column(String(200), nullable=True)
    price_estimate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str | None] = mapped_column(String(30), nullable=True)

    __table_args__ = (
        CheckConstraint("price_estimate >= 0", name="ck_wishes_price_non_negative"),
    )
