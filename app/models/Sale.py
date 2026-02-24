from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.core.db import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    products = relationship(
        "Product",
        secondary="sale_items",
        back_populates="sales",
        viewonly=True,
    )
    user = relationship("User", back_populates="sales")
