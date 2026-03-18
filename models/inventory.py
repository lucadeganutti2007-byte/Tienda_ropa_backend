import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from db.database import Base

class MovementType(str, enum.Enum):
    in_purchase = "in_purchase"       # From a purchase order
    out_sale_online = "out_sale_online" # E-commerce sale
    out_sale_internal = "out_sale_internal" # Backoffice manual sale
    adjustment = "adjustment"         # Manual adjustment (loss, recount)

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False) # Can be positive or negative
    movement_type = Column(Enum(MovementType), nullable=False)
    reference_id = Column(Integer, nullable=True) # ID of Sale or PurchaseOrder
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Who made the adjustment/movement

    variant = relationship("ProductVariant", back_populates="inventory_movements")
    created_by = relationship("User")
