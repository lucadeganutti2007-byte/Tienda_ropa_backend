from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.db import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    size = Column(String, nullable=False)
    color = Column(String, nullable=False)
    price_override = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)

    product = relationship("Product", back_populates="variants")
    images = relationship(
        "ProductImage",
        back_populates="product_variant",
        cascade="all, delete-orphan",
        order_by="ProductImage.position",
    )
