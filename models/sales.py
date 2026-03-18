import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship
from db.database import Base

class SaleType(str, enum.Enum):
    online = "online"
    internal = "internal"

class SaleStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    preparing = "preparing"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Optional for anonymous in-store
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True) # For internal sales, who created it
    sale_type = Column(Enum(SaleType), nullable=False)
    status = Column(Enum(SaleStatus), default=SaleStatus.pending, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    shipping_address = Column(String, nullable=True)
    mp_preference_id = Column(String, nullable=True)
    mp_payment_id = Column(String, nullable=True)

    customer = relationship("User", foreign_keys=[customer_id])
    seller = relationship("User", foreign_keys=[seller_id])
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="items")
    variant = relationship("ProductVariant", back_populates="sale_items")
