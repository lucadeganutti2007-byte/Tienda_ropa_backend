from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.sales import SaleType, SaleStatus
from schemas.user import User

class SaleItemBase(BaseModel):
    variant_id: int
    quantity: int
    unit_price: float

class SaleItemCreate(SaleItemBase):
    pass

class SaleItem(SaleItemBase):
    id: int
    sale_id: int

    class Config:
        from_attributes = True

class SaleBase(BaseModel):
    sale_type: SaleType = SaleType.online
    shipping_address: Optional[str] = None

class SaleCreate(SaleBase):
    items: List[SaleItemCreate]

class Sale(SaleBase):
    id: int
    customer_id: Optional[int] = None
    seller_id: Optional[int] = None
    status: SaleStatus
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[SaleItem] = []

    class Config:
        from_attributes = True
