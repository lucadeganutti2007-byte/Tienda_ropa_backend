from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.purchasing import OrderStatus

# --- Supplier ---
class SupplierBase(BaseModel):
    name: str
    contact_info: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class Supplier(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Purchase Order Item ---
class PurchaseOrderItemBase(BaseModel):
    variant_id: int
    quantity: int
    unit_cost: float

class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    pass

class PurchaseOrderItem(PurchaseOrderItemBase):
    id: int
    order_id: int
    received_quantity: int = 0

    class Config:
        from_attributes = True

# --- Purchase Order ---
class PurchaseOrderBase(BaseModel):
    supplier_id: int
    notes: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderReceive(BaseModel):
    """Used when receiving goods from a purchase order."""
    items: List[dict]  # [{"item_id": 1, "received_quantity": 10}, ...]

class PurchaseOrder(PurchaseOrderBase):
    id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[PurchaseOrderItem] = []
    supplier: Optional[Supplier] = None

    class Config:
        from_attributes = True
