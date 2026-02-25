from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.db import Base


class ProductImage(Base):
    __tablename__ = "product_images"
    __table_args__ = (
        CheckConstraint("position >= 1 AND position <= 8", name="ck_product_images_position_1_8"),
        UniqueConstraint("product_variant_id", "position", name="uq_variant_image_position"),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False, index=True)
    image_url = Column(String, nullable=False)
    position = Column(Integer, nullable=False)

    product_variant = relationship("ProductVariant", back_populates="images")
