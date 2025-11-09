from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field


class Wish(BaseModel):
    model_config = dict(extra="forbid")

    id: int
    title: Annotated[str, Field(min_length=1, max_length=50)]
    link: str | None = Field(default=None, max_length=200)
    price_estimate: (
        Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)] | None
    ) = None
    notes: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=30)
    owner: str | None = None
