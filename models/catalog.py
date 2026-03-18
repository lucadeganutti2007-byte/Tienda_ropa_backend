from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from db.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    base_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    color = Column(String, nullable=False)
    size = Column(String, nullable=False)
    price_override = Column(Float, nullable=True) # If null, use product.base_price
    min_stock = Column(Integer, default=5, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="variants")
    inventory_movements = relationship("InventoryMovement", back_populates="variant")
    sale_items = relationship("SaleItem", back_populates="variant")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="variant")

    @property
    def price(self):
        return self.price_override if self.price_override is not None else self.product.base_price
