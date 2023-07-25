from typing import Optional

from pydantic import BaseModel


class Example(BaseModel):
    str_field: str
    int_field: int
    float_field: float
    list_of_ints: list[int]
    list_of_nullable: list[str | None]
    optional: Optional[bool]
