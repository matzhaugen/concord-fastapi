from datetime import date
from typing import List, Optional

from pydantic import BaseModel


def to_camel(string: str) -> str:
    result = "".join(word.capitalize() for word in string.split("_"))
    result = result[0].lower() + result[1:]
    return result


class PortfolioRequest(BaseModel):
    tickers: List[str]
    end_date: date

    class Config:
        schema_extra = {"example": {"tickers": ["AA", "AXP"], "endDate": "1993-01-01"}}
        alias_generator = to_camel
        allow_population_by_field_name = True


class StockDate(BaseModel):
    ticker: str
    date: date
    price: float


class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True
