from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    url: str
    title: str
    price: Optional[float] = None
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True