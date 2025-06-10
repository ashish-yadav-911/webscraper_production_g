from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    url: str
    title: str
    price: Optional[float] = None
    description: Optional[str] = None
    # --- ADD THIS LINE ---
    image_url: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True # Changed from orm_mode for Pydantic v2