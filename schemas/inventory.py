from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.inventory import MovementType

class InventoryMovementBase(BaseModel):
    variant_id: int
    quantity: int
    movement_type: MovementType
    notes: Optional[str] = None

class InventoryMovementCreate(InventoryMovementBase):
    pass

class InventoryMovement(InventoryMovementBase):
    id: int
    reference_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StockLevel(BaseModel):
    variant_id: int
    sku: str
    product_name: str
    color: str
    size: str
    current_stock: int
    min_stock: int
    is_low: bool
