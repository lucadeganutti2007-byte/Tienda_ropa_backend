from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    items = relationship("SaleItem", back_populates="product")
    sales = relationship(
        "Sale",
        secondary="sale_items",
        back_populates="products",
        viewonly=True,
    )
    category = relationship("Category", back_populates="products")
    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan",
    )
