from typing import Annotated

from pydantic import BaseModel, Field


class Wish(BaseModel):
    id: int
    title: Annotated[str, Field(min_length=1, max_length=50)]
    link: str | None = Field(default=None, max_length=200)
    price_estimate: Annotated[float, Field(ge=0)] | None = None
    notes: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=30)
    owner: str | None = None
